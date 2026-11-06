from uuid import uuid4

from database import save_geracao


def registrar_geracao(
    resultado_pipeline,
    usuario_id="teste_local",
    sessao_id="sessao_teste",
):
    geracao_id = str(uuid4())

    save_geracao(
        gid=geracao_id,
        user=usuario_id,
        session=sessao_id,
        pacote=resultado_pipeline.pacote,
        duracao_ms=resultado_pipeline.duracao_ms,
    )

    return geracao_id