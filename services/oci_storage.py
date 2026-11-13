"""Upload de resultados para o OCI Object Storage.

Responsabilidade:
  - Recebe o JSON de resultado gerado pelo pipeline RAG.
  - Envia para o bucket OCI configurado em OCI_BUCKET_ARTIFACTS.
  - Se a OCI estiver indisponível (sem config, sem rede), salva localmente como fallback.
  - Retorna sempre um dicionário compatível com o campo `armazenamento_oci` da saída JSON.

Requisito NoCountry: o campo `armazenamento_oci` da saída JSON deve conter:
  {
    "bucket": "mentoria-tech-artifacts",
    "objeto_id": "<nome-do-objeto>",
    "status_upload": "concluido" | "fallback_local" | "erro"
  }

Uso:
    from services.oci_storage import enviar_resultado
    info = enviar_resultado(payload_json, nome_objeto="resultado-123.json")
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
_env_path = Path(__file__).parent.parent / "rag" / ".env"
if not _env_path.exists():
    _env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=False)

# Configurações lidas do ambiente
_BUCKET = os.getenv("OCI_BUCKET_ARTIFACTS", "mentoria-tech-artifacts")
_NAMESPACE = os.getenv("OCI_NAMESPACE", "")
_PROFILE = os.getenv("OCI_PROFILE", "MENTORIA_TECH")
_USE_OCI = os.getenv("USE_OCI_VAULT", "false").lower() != "true"

# Pasta de fallback local (dentro de data/bi_exports/)
_PASTA_FALLBACK = Path(__file__).parent.parent / "data" / "oci_fallback"


def _gerar_nome_objeto(prefixo: str = "resultado") -> str:
    """Gera um nome único para o objeto no bucket com timestamp UTC."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefixo}_{ts}.json"


def _salvar_localmente(payload: dict, nome_objeto: str) -> dict:
    """Salva o resultado localmente como fallback quando OCI está indisponível."""
    _PASTA_FALLBACK.mkdir(parents=True, exist_ok=True)
    caminho = _PASTA_FALLBACK / nome_objeto
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    logger.warning("OCI indisponível — resultado salvo localmente em: %s", caminho)
    return {
        "bucket": _BUCKET,
        "objeto_id": nome_objeto,
        "status_upload": "fallback_local",
        "caminho_local": str(caminho),
    }


def _obter_cliente_e_namespace():
    """Obtém cliente OCI e namespace suportando Streamlit Secrets e ~/.oci/config."""
    try:
        import oci
    except ImportError:
        return None, ""

    # 1. Tenta carregar via Streamlit Secrets (ambiente Streamlit Cloud)
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "oci" in st.secrets:
            sec = dict(st.secrets["oci"])
            config = {
                "user": sec.get("user"),
                "fingerprint": sec.get("fingerprint"),
                "key_content": sec.get("key_content"),
                "tenancy": sec.get("tenancy"),
                "region": sec.get("region", "sa-saopaulo-1"),
            }
            oci.config.validate_config(config)
            ns = sec.get("namespace", _NAMESPACE)
            return oci.object_storage.ObjectStorageClient(config), ns
    except Exception:
        pass

    # 2. Tenta carregar via arquivo ~/.oci/config (ambiente local do desenvolvedor)
    try:
        config = oci.config.from_file(profile_name=_PROFILE)
        ns = _NAMESPACE or config.get("namespace", "")
        return oci.object_storage.ObjectStorageClient(config), ns
    except Exception:
        pass

    return None, ""


def _tentar_upload_oci(payload: dict, nome_objeto: str) -> dict:
    """Tenta enviar o payload para o OCI Object Storage via SDK ou PAR."""
    conteudo = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

    # 1. Opção via Pre-Authenticated Request (PAR), se configurada
    par_base = os.getenv("OCI_PAR_URL", "")
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "OCI_PAR_URL" in st.secrets:
            par_base = st.secrets["OCI_PAR_URL"]
    except Exception:
        pass

    if par_base:
        try:
            import urllib.request
            url = par_base.rstrip("/") + "/" + nome_objeto
            req = urllib.request.Request(url, data=conteudo, method="PUT")
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status in (200, 201):
                    logger.info("Upload OCI via PAR concluído: %s", nome_objeto)
                    return {
                        "bucket": _BUCKET,
                        "objeto_id": nome_objeto,
                        "status_upload": "concluido",
                    }
        except Exception as exc_par:
            logger.warning("Falha no upload via PAR (%s). Tentando SDK...", exc_par)

    # 2. Opção via SDK OCI (Streamlit Secrets em memória ou ~/.oci/config local)
    try:
        cliente, ns = _obter_cliente_e_namespace()
        if cliente:
            cliente.put_object(
                namespace_name=ns,
                bucket_name=_BUCKET,
                object_name=nome_objeto,
                put_object_body=conteudo,
                content_type="application/json",
            )
            logger.info("Upload OCI concluído via SDK: bucket=%s, objeto=%s", _BUCKET, nome_objeto)
            return {
                "bucket": _BUCKET,
                "objeto_id": nome_objeto,
                "status_upload": "concluido",
            }
        else:
            logger.warning("Nenhuma credencial OCI encontrada. Usando fallback local.")
            return _salvar_localmente(payload, nome_objeto)

    except Exception as exc:  # noqa: BLE001
        logger.warning("Erro ao conectar na OCI (%s). Usando fallback local.", exc)
        return _salvar_localmente(payload, nome_objeto)


def enviar_resultado(payload: dict, nome_objeto: str | None = None) -> dict:
    """Envia o resultado do pipeline para o OCI Object Storage.

    Args:
        payload: Dicionário com o resultado completo gerado pelo pipeline RAG.
        nome_objeto: Nome do objeto no bucket. Se None, gera automaticamente com timestamp.

    Returns:
        Dicionário com `bucket`, `objeto_id` e `status_upload` para compor a saída JSON.
    """
    if nome_objeto is None:
        nome_objeto = _gerar_nome_objeto()

    # Verifica se o perfil OCI está minimamente configurado
    if not _NAMESPACE and not _PROFILE:
        logger.warning("OCI não configurada (OCI_NAMESPACE e OCI_PROFILE ausentes). Fallback local.")
        return _salvar_localmente(payload, nome_objeto)

    return _tentar_upload_oci(payload, nome_objeto)

