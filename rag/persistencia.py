from uuid import uuid4

from database import (
    save_geracao,
    save_avaliacao_documento,
    get_avaliacao_documento,
    save_telemetria_api,
    get_telemetria_execucao,
)


def registrar_geracao(
    resultado_pipeline,
    usuario_id="teste_local",
    sessao_id="sessao_teste",
    avaliacao_id=None,
):
    geracao_id = str(uuid4())

    save_geracao(
        gid=geracao_id,
        user=usuario_id,
        session=sessao_id,
        pacote=resultado_pipeline.pacote,
        duracao_ms=resultado_pipeline.duracao_ms,
        avaliacao_id=avaliacao_id,
    )

    return geracao_id

# ============================================================
# PERSISTÊNCIA DA AVALIAÇÃO DO DOCUMENTO
# ============================================================

def registrar_avaliacao_documento(
    documento_id,
    documento_hash,
    perfis_compativeis,
    niveis_compativeis,
    **dados_adicionais,
):
    avaliacao_id = str(uuid4())

    save_avaliacao_documento(
        avaliacao_id=avaliacao_id,
        documento_id=documento_id,
        documento_hash=documento_hash,
        perfis_compativeis=perfis_compativeis,
        niveis_compativeis=niveis_compativeis,
        **dados_adicionais,
    )

    return avaliacao_id


# ============================================================
# PERSISTÊNCIA DA TELEMETRIA
# ============================================================

def registrar_telemetria_api(
    execucao_id,
    provedor,
    modelo,
    operacao,
    status,
    **dados_adicionais,
):
    chamada_id = str(uuid4())

    save_telemetria_api(
        chamada_id=chamada_id,
        execucao_id=execucao_id,
        provedor=provedor,
        modelo=modelo,
        operacao=operacao,
        status=status,
        **dados_adicionais,
    )

    return chamada_id
