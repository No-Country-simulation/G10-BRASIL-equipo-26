"""Cliente HTTP para comunicação com a API FastAPI do MentorIA Tech (contrato v0.3)."""

import json
from pathlib import Path
from typing import Any

import requests

from config import (
    MIME_POR_EXTENSAO,
    TIMEOUT_GERACAO,
    TIMEOUT_HEALTH,
    TIMEOUT_PADRAO,
    obter_api_base_url,
)


class ApiError(Exception):
    """Erro estruturado retornado nas chamadas à API FastAPI."""

    def __init__(
        self,
        status: int | None,
        detalhe: str,
        mensagem_amigavel: str,
        detalhes_tecnicos: str = "",
    ) -> None:
        super().__init__(mensagem_amigavel)
        self.status = status
        self.detalhe = detalhe
        self.mensagem_amigavel = mensagem_amigavel
        self.detalhes_tecnicos = detalhes_tecnicos


def criar_session() -> requests.Session:
    """Cria uma sessão HTTP reutilizável para as chamadas do frontend."""
    return requests.Session()


def _extrair_detalhe(resp: requests.Response) -> str:
    """Extrai mensagem de erro de `detail` (string ou lista Pydantic) ou texto bruto."""
    try:
        payload = resp.json()
    except ValueError:
        texto = (resp.text or "").strip()
        return texto[:500] if texto else f"HTTP {resp.status_code}"

    if isinstance(payload, dict) and "detail" in payload:
        detail = payload["detail"]
        if isinstance(detail, str):
            return detail
        if isinstance(detail, list):
            partes: list[str] = []
            for item in detail:
                if isinstance(item, dict):
                    loc = ".".join(str(x) for x in item.get("loc", []))
                    msg = str(item.get("msg", item))
                    partes.append(f"{loc}: {msg}" if loc else msg)
                else:
                    partes.append(str(item))
            return "; ".join(partes) if partes else f"HTTP {resp.status_code}"
        return json.dumps(detail, ensure_ascii=False)

    return json.dumps(payload, ensure_ascii=False)[:500]


def _traduzir_erro_http(status: int, detalhe: str) -> str:
    """Mapeia códigos HTTP do contrato v0.3 para mensagens amigáveis ao usuário."""
    detalhe_lower = detalhe.lower()
    if status == 400:
        if "não é um quiz" in detalhe_lower or "nao e um quiz" in detalhe_lower:
            return "A geração selecionada não é um Quiz."
        if "rodada" in detalhe_lower:
            return "Rodada não registrada ou expirada. Inicie uma nova rodada."
        return f"Requisição inválida: {detalhe}"
    if status == 404:
        return "Quiz não encontrado ou não associado ao seu ID anônimo atual."
    if status == 409:
        return "Questão já encerrada nesta rodada (acerto ou limite de 3 tentativas atingido)."
    if status == 413:
        return "Arquivo vazio ou maior que o limite permitido de 20 MiB."
    if status == 422:
        return f"Dados ou arquivo inválidos: {detalhe}"
    if status == 500:
        return "Falha interna no servidor durante a geração. Consulte os logs da API e tente novamente."
    if status == 503:
        return "Serviço de IA indisponível: verifique a chave Gemini configurada no backend (rag/.env)."
    return f"Erro HTTP {status}: {detalhe}"


def _tratar_resposta(resp: requests.Response) -> Any:
    """Valida a resposta HTTP e converte falhas em `ApiError`."""
    if not resp.ok:
        detalhe = _extrair_detalhe(resp)
        raise ApiError(
            status=resp.status_code,
            detalhe=detalhe,
            mensagem_amigavel=_traduzir_erro_http(resp.status_code, detalhe),
            detalhes_tecnicos=(resp.text or "")[:1000],
        )

    try:
        return resp.json()
    except ValueError as exc:
        raise ApiError(
            status=resp.status_code,
            detalhe="Resposta não JSON",
            mensagem_amigavel="O servidor retornou uma resposta inválida (não JSON).",
            detalhes_tecnicos=(resp.text or str(exc))[:1000],
        ) from exc


def _executar_request(
    method: str,
    endpoint: str,
    timeout: tuple[int, int],
    base_url: str | None = None,
    session: requests.Session | None = None,
    **kwargs: Any,
) -> Any:
    """Executa requisição HTTP tratando falhas de rede e timeouts."""
    url_base = (base_url or obter_api_base_url()).rstrip("/")
    url = f"{url_base}{endpoint}"
    sess = session or requests.Session()

    try:
        resp = sess.request(method, url, timeout=timeout, **kwargs)
    except requests.exceptions.ConnectionError as exc:
        raise ApiError(
            status=None,
            detalhe="ConnectionError",
            mensagem_amigavel=f"Não foi possível conectar à API em {url_base}. Verifique se o backend FastAPI está rodando.",
            detalhes_tecnicos=str(exc),
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise ApiError(
            status=None,
            detalhe="Timeout",
            mensagem_amigavel="A requisição excedeu o tempo limite. Tente reduzir a quantidade de itens ou aguarde a conclusão no servidor.",
            detalhes_tecnicos=str(exc),
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise ApiError(
            status=None,
            detalhe=type(exc).__name__,
            mensagem_amigavel=f"Erro de comunicação com a API: {exc}",
            detalhes_tecnicos=str(exc),
        ) from exc

    return _tratar_resposta(resp)


def verificar_saude(
    base_url: str | None = None,
    session: requests.Session | None = None,
) -> bool:
    """Verifica se a API está acessível via `GET /health`."""
    try:
        dados = _executar_request(
            "GET",
            "/health",
            timeout=TIMEOUT_HEALTH,
            base_url=base_url,
            session=session,
        )
        return isinstance(dados, dict) and dados.get("status") == "ok"
    except ApiError:
        return False


def gerar_conteudo(
    arquivo_nome: str,
    arquivo_bytes: bytes,
    perfil: str,
    nivel: str,
    formato: str,
    quantidade_itens: int,
    usuario_id: str,
    sessao_id: str,
    base_url: str | None = None,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    """Envia documento em `multipart/form-data` para `POST /geracoes`."""
    ext = Path(arquivo_nome).suffix.lower()
    mime = MIME_POR_EXTENSAO.get(ext, "application/octet-stream")
    files = {"arquivo": (arquivo_nome, arquivo_bytes, mime)}
    data = {
        "perfil": perfil,
        "nivel": nivel,
        "formato": formato,
        "quantidade_itens": str(quantidade_itens),
        "usuario_id": usuario_id,
        "sessao_id": sessao_id,
    }
    return _executar_request(
        "POST",
        "/geracoes",
        timeout=TIMEOUT_GERACAO,
        base_url=base_url,
        session=session,
        files=files,
        data=data,
    )


def listar_quizzes(
    usuario_id: str,
    base_url: str | None = None,
    session: requests.Session | None = None,
) -> list[dict[str, Any]]:
    """Lista até 30 quizzes recentes do usuário via `GET /quiz`."""
    return _executar_request(
        "GET",
        "/quiz",
        timeout=TIMEOUT_PADRAO,
        base_url=base_url,
        session=session,
        params={"usuario_id": usuario_id},
    )


def consultar_quiz(
    geracao_id: str,
    usuario_id: str,
    base_url: str | None = None,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    """Consulta questões públicas (sem gabarito) via `GET /quiz/{geracao_id}`."""
    return _executar_request(
        "GET",
        f"/quiz/{geracao_id}",
        timeout=TIMEOUT_PADRAO,
        base_url=base_url,
        session=session,
        params={"usuario_id": usuario_id},
    )


def iniciar_rodada(
    geracao_id: str,
    usuario_id: str,
    sessao_id: str,
    base_url: str | None = None,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    """Inicia uma nova rodada de Quiz via `POST /quiz/rodadas`."""
    return _executar_request(
        "POST",
        "/quiz/rodadas",
        timeout=TIMEOUT_PADRAO,
        base_url=base_url,
        session=session,
        json={
            "geracao_id": geracao_id,
            "usuario_id": usuario_id,
            "sessao_id": sessao_id,
        },
    )


def responder_questao(
    geracao_id: str,
    usuario_id: str,
    sessao_id: str,
    rodada_id: str,
    questao_indice: int,
    alternativa_escolhida: int,
    tempo_resposta_segundos: float = 0.0,
    base_url: str | None = None,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    """Registra resposta de uma questão via `POST /quiz/respostas`."""
    return _executar_request(
        "POST",
        "/quiz/respostas",
        timeout=TIMEOUT_PADRAO,
        base_url=base_url,
        session=session,
        json={
            "geracao_id": geracao_id,
            "usuario_id": usuario_id,
            "sessao_id": sessao_id,
            "rodada_id": rodada_id,
            "questao_indice": questao_indice,
            "alternativa_escolhida": alternativa_escolhida,
            "tempo_resposta_segundos": max(0.0, float(tempo_resposta_segundos)),
        },
    )


def obter_historico(
    geracao_id: str,
    usuario_id: str,
    base_url: str | None = None,
    session: requests.Session | None = None,
) -> list[dict[str, Any]]:
    """Consulta até 100 tentativas recentes via `GET /quiz/{geracao_id}/historico`."""
    return _executar_request(
        "GET",
        f"/quiz/{geracao_id}/historico",
        timeout=TIMEOUT_PADRAO,
        base_url=base_url,
        session=session,
        params={"usuario_id": usuario_id},
    )
