
import time
from contextvars import ContextVar

from persistencia import registrar_telemetria_api


_execucao_atual = ContextVar(
    "novamente_execucao_atual",
    default=None,
)

_tentativa_atual = ContextVar(
    "novamente_tentativa_atual",
    default=None,
)


def definir_execucao(execucao_id):
    """Associa uma execução ao contexto atual."""
    return _execucao_atual.set(execucao_id)


def restaurar_execucao(token):
    """Restaura o contexto anterior."""
    _execucao_atual.reset(token)


def iniciar_tentativa():
    """Inicia a coleta de chamadas de uma geração."""
    chamadas = []
    token = _tentativa_atual.set(chamadas)
    return chamadas, token


def finalizar_tentativa(token):
    """Restaura o contexto anterior da tentativa."""
    _tentativa_atual.reset(token)


def registrar_chamada(
    provedor,
    modelo,
    operacao,
    inicio,
    status,
    tokens_entrada=None,
    tokens_saida=None,
    tokens_totais=None,
    codigo_http=None,
):
    """Registra uma tentativa de API sem interromper a geração."""

    execucao_id = _execucao_atual.get()

    if execucao_id is None:
        return

    duracao_ms = (time.perf_counter() - inicio) * 1000

    try:
        chamada_id = registrar_telemetria_api(
            execucao_id=execucao_id,
            provedor=provedor,
            modelo=modelo,
            operacao=operacao,
            status=status,
            tokens_entrada=tokens_entrada,
            tokens_saida=tokens_saida,
            tokens_totais=tokens_totais,
            duracao_ms=duracao_ms,
            codigo_http=codigo_http,
        )

        chamadas = _tentativa_atual.get()

        if chamadas is not None:
            chamadas.append(chamada_id)

    except Exception as exc:
        print(
            "Aviso: falha ao registrar telemetria:",
            type(exc).__name__,
            str(exc),
        )
