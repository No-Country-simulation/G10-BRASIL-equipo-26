"""Ponte entre o frontend Streamlit e o módulo `services/oci_storage.py`."""

import os
import sys
from typing import Any

from config import REPO_DIR, obter_bucket_artefatos, obter_config

# Sincroniza configurações do Streamlit Secrets para os envs lidos por services/oci_storage.py
for _chave_oci in ("OCI_BUCKET_ARTIFACTS", "OCI_NAMESPACE", "OCI_PROFILE", "USE_OCI_VAULT"):
    if not os.getenv(_chave_oci):
        _valor = obter_config(_chave_oci)
        if _valor:
            os.environ[_chave_oci] = _valor

if str(REPO_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_DIR))

OCI_DISPONIVEL = False
_oci_storage_mod = None
_enviar_resultado_fn = None

try:
    from services import oci_storage as _oci_storage_mod  # type: ignore[no-redef]
    from services.oci_storage import enviar_resultado as _enviar_resultado_fn  # type: ignore[no-redef]

    OCI_DISPONIVEL = True
except Exception:
    OCI_DISPONIVEL = False
    _oci_storage_mod = None
    _enviar_resultado_fn = None


def montar_pacote_artefato(resultado: dict[str, Any]) -> dict[str, Any]:
    """
    Monta o JSON estruturado do artefato para persistência na OCI e exportação.

    Não inclui `usuario_id` (privacidade) nem gabarito antecipado para Quiz.
    """
    formato = resultado.get("formato", "")
    if formato == "Quiz":
        conteudo_adaptado: dict[str, Any] = {
            "formato": "Quiz",
            "questoes": resultado.get("questoes") or [],
        }
    else:
        conteudo_adaptado = resultado.get("conteudo") or {}

    pacote: dict[str, Any] = {
        "status": "sucesso",
        "geracao_id": resultado.get("id"),
        "avaliacao_id": resultado.get("avaliacao_id"),
        "entrada": {
            "documento": resultado.get("documento_nome"),
            "perfil": resultado.get("perfil"),
            "nivel": resultado.get("nivel"),
            "formato": formato,
            "quantidade_itens": resultado.get("quantidade_itens"),
        },
        "metadados": {
            "duracao_ms": resultado.get("duracao_ms"),
            "adequacao": resultado.get("adequacao"),
            "gerado_em": resultado.get("criado_em"),
        },
        "conteudo_adaptado": conteudo_adaptado,
    }
    if resultado.get("armazenamento_oci"):
        pacote["armazenamento_oci"] = resultado["armazenamento_oci"]
    return pacote


def persistir_artefato(resultado: dict[str, Any]) -> dict[str, Any]:
    """Envia o pacote estruturado ao OCI Object Storage via `services.oci_storage`."""
    geracao_id = resultado.get("id", "sem_id")
    nome_objeto = f"resultado_{geracao_id}.json"
    pacote = montar_pacote_artefato(resultado)

    if not OCI_DISPONIVEL or _enviar_resultado_fn is None:
        info = {
            "bucket": obter_bucket_artefatos(),
            "objeto_id": nome_objeto,
            "status_upload": "erro",
            "erro": "Módulo services.oci_storage indisponível neste ambiente.",
        }
        resultado["armazenamento_oci"] = info
        return info

    try:
        info = _enviar_resultado_fn(pacote, nome_objeto=nome_objeto)
    except Exception as exc:
        info = {
            "bucket": obter_bucket_artefatos(),
            "objeto_id": nome_objeto,
            "status_upload": "erro",
            "erro": str(exc),
        }

    resultado["armazenamento_oci"] = info
    return info


def persistir_documento_original(nome_arquivo: str, dados: bytes) -> dict[str, Any] | None:
    """Envia documento original para OCI se o serviço suportar upload binário."""
    if OCI_DISPONIVEL and _oci_storage_mod is not None and hasattr(_oci_storage_mod, "enviar_documento"):
        try:
            return _oci_storage_mod.enviar_documento(dados, nome_objeto=nome_arquivo)
        except Exception as exc:
            return {"status_upload": "erro", "objeto_id": nome_arquivo, "erro": str(exc)}
    return None


def rotulo_status_oci(armazenamento: dict[str, Any] | None) -> tuple[str, str]:
    """Retorna `(badge_curto, descricao)` amigáveis para exibição na UI."""
    if not armazenamento:
        return ("⏳ Pendente", "Aguardando persistência no bucket OCI.")

    status = str(armazenamento.get("status_upload", "")).lower()
    bucket = armazenamento.get("bucket") or obter_bucket_artefatos()
    objeto = armazenamento.get("objeto_id", "")

    if status in ("concluido", "sucesso"):
        return ("✅ OCI Bucket", f"Enviado para `{bucket}/{objeto}`.")
    if status == "fallback_local":
        caminho = armazenamento.get("caminho_local", "data/oci_fallback")
        return ("⚠️ Fallback Local", f"OCI indisponível; salvo localmente em `{caminho}`.")
    erro = armazenamento.get("erro", "Falha desconhecida no upload.")
    return ("❌ Erro OCI", f"Não foi possível persistir no bucket `{bucket}`: {erro}")
