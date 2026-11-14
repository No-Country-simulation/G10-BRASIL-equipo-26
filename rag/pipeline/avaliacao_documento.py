
from pipeline.schemas import (
    AvaliacaoAdequacaoDocumento,
    ResultadoAdequacaoSolicitacao,
    Perfil,
    Dificuldade,
)

def comparar_adequacao(
    avaliacao: AvaliacaoAdequacaoDocumento,
    perfil_solicitado: Perfil,
    nivel_solicitado: Dificuldade,
) -> ResultadoAdequacaoSolicitacao:

    if avaliacao.status != "avaliado":
        return ResultadoAdequacaoSolicitacao(
            perfil_solicitado=perfil_solicitado,
            nivel_solicitado=nivel_solicitado,
            perfil_compativel=None,
            nivel_compativel=None,
            divergencia=None,
            mensagem=(
                "Não foi possível determinar a adequação "
                "do documento à solicitação."
            ),
        )

    perfil_compativel = (
        perfil_solicitado in avaliacao.perfis_compativeis
    )

    nivel_compativel = (
        nivel_solicitado in avaliacao.niveis_compativeis
    )

    divergencia = not (
        perfil_compativel and nivel_compativel
    )

    mensagem = None

    if divergencia:
        perfis = ", ".join(
            perfil.value for perfil in avaliacao.perfis_compativeis
        ) or "não determinados"

        niveis = ", ".join(
            nivel.value for nivel in avaliacao.niveis_compativeis
        ) or "não determinados"

        mensagem = (
            "O documento pode não oferecer a profundidade "
            "ou abordagem esperada para a solicitação. "
            f"Perfis compatíveis: {perfis}. "
            f"Níveis compatíveis: {niveis}. "
            "Você pode manter suas escolhas."
        )

    return ResultadoAdequacaoSolicitacao(
        perfil_solicitado=perfil_solicitado,
        nivel_solicitado=nivel_solicitado,
        perfil_compativel=perfil_compativel,
        nivel_compativel=nivel_compativel,
        divergencia=divergencia,
        mensagem=mensagem,
    )


# ============================================================
# AVALIAÇÃO REAL DO DOCUMENTO — GEMINI + CACHE SQLITE
# ============================================================

import hashlib
import json
import os
import time
from uuid import uuid4

from pydantic import ValidationError

from database import get_avaliacao_documento
from persistencia import (
    registrar_avaliacao_documento,
    registrar_telemetria_api,
)

from pipeline.schemas import DocumentoExtraido


VERSAO_AVALIADOR = "1"
MAX_CARACTERES_AVALIACAO = 18000


def calcular_hash_documento(documento: DocumentoExtraido) -> str:
    """Identifica o conteúdo textual extraído, independentemente do nome."""
    partes = [
        f"{pagina.pagina}:{pagina.texto}"
        for pagina in sorted(
            documento.paginas,
            key=lambda p: p.pagina,
        )
    ]
    conteudo = "\n".join(partes)
    return hashlib.sha256(conteudo.encode("utf-8")).hexdigest()


def selecionar_texto_avaliacao(
    documento: DocumentoExtraido,
    limite: int = MAX_CARACTERES_AVALIACAO,
) -> str:
    """Distribui o orçamento de texto entre as páginas do documento."""
    paginas = sorted(documento.paginas, key=lambda p: p.pagina)

    if not paginas:
        return ""

    partes = []
    quota = max(1, limite // len(paginas))

    for pagina in paginas:
        texto = pagina.texto.strip()

        if not texto:
            continue

        # Para páginas longas, amostra início, meio e fim.
        if len(texto) > quota:
            bloco = max(1, quota // 3)
            meio = len(texto) // 2

            texto = "\n[...]\n".join([
                texto[:bloco],
                texto[max(0, meio - bloco // 2):meio + bloco // 2],
                texto[-bloco:],
            ])

        partes.append(f"[PÁGINA {pagina.pagina}]\n{texto}")

    return "\n\n".join(partes)[:limite]


def _avaliacao_do_cache(registro):
    if not registro or registro["status"] != "avaliado":
        return None

    try:
        return AvaliacaoAdequacaoDocumento.model_validate({
            "perfis_compativeis": registro["perfis_compativeis"],
            "niveis_compativeis": registro["niveis_compativeis"],
            "perfil_recomendado": registro["perfil_recomendado"],
            "nivel_recomendado": registro["nivel_recomendado"],
            "justificativa": registro["justificativa"],
            "evidencias": registro["evidencias_json"],
            "status": registro["status"],
            "modelo_avaliador": registro["modelo_avaliador"],
        })
    except ValidationError:
        return None


def avaliar_documento(
    documento: DocumentoExtraido,
    execucao_id: str | None = None,
) -> tuple[str, AvaliacaoAdequacaoDocumento]:
    """
    Retorna (avaliacao_id, avaliacao).

    Cache válido: zero chamadas de API.
    Cache ausente: no máximo uma requisição Gemini.
    Falha: avaliação indisponível, sem impedir a geração.
    """
    documento_hash = calcular_hash_documento(documento)

    registro = get_avaliacao_documento(
        documento_hash,
        VERSAO_AVALIADOR,
    )

    avaliacao_cache = _avaliacao_do_cache(registro)

    if avaliacao_cache is not None:
        return registro["avaliacao_id"], avaliacao_cache

    from google import genai
    from google.genai import types

    # Reutiliza a configuração de chaves já existente no projeto,
    # mas não utiliza os retries de chamar_gemini().
    from pipeline.llm_pipeline import _chaves_api

    chaves = _chaves_api("GEMINI")
    modelo = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    avaliacao = AvaliacaoAdequacaoDocumento(
        status="indisponivel"
    )

    texto = selecionar_texto_avaliacao(documento)

    system = """
Você avalia a adequação pedagógica de documentos técnicos.

Classifique exclusivamente com base nas evidências do texto.

Perfis permitidos:
- Iniciante
- Jr/Pleno
- Tech Lead
- Gestor

Níveis permitidos:
- basico
- intermediario
- avancado

Um documento pode ser compatível com vários perfis e níveis.
Avalie a profundidade oferecida pelo documento, não a capacidade
ou o direito de uma pessoa estudar o material.

Se a amostra não permitir uma conclusão confiável,
retorne status "inconclusivo".

Responda SOMENTE com um objeto JSON contendo:
perfis_compativeis (lista),
niveis_compativeis (lista),
perfil_recomendado (string ou null),
nivel_recomendado (string ou null),
justificativa (string ou null),
evidencias (lista de strings),
status ("avaliado" ou "inconclusivo").

Não invente evidências.
"""

    user = (
        "Avalie a adequação pedagógica do seguinte documento.\n\n"
        + texto
    )

    if chaves and texto:
        client = None
        inicio = time.perf_counter()

        tokens_entrada = None
        tokens_saida = None
        tokens_totais = None
        codigo_http = None
        status_chamada = "erro"

        try:
            client = genai.Client(
                api_key=chaves[0],
                http_options=types.HttpOptions(timeout=60000),
            )

            response = client.models.generate_content(
                model=modelo,
                contents=user,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    response_mime_type="application/json",
                    temperature=0,
                    max_output_tokens=1200,
                ),
            )

            uso = response.usage_metadata

            if uso is not None:
                tokens_entrada = uso.prompt_token_count
                tokens_saida = uso.candidates_token_count
                tokens_totais = uso.total_token_count

            if not response.text:
                raise ValueError("Resposta vazia do Gemini.")

            dados = json.loads(response.text)
            dados["modelo_avaliador"] = modelo

            avaliacao = AvaliacaoAdequacaoDocumento.model_validate(
                dados
            )

            status_chamada = "sucesso"

        except Exception as exc:
            codigo_http = getattr(exc, "code", None)
            print(
                "Aviso: avaliação do documento indisponível: "
                f"{type(exc).__name__}: {exc}"
            )

        finally:
            duracao_ms = (
                time.perf_counter() - inicio
            ) * 1000

            if client is not None:
                client.close()

            if execucao_id is not None:
                registrar_telemetria_api(
                    execucao_id=execucao_id,
                    provedor="Gemini",
                    modelo=modelo,
                    operacao="avaliacao_documento",
                    status=status_chamada,
                    documento_id=documento.documento.documento_id,
                    tokens_entrada=tokens_entrada,
                    tokens_saida=tokens_saida,
                    tokens_totais=tokens_totais,
                    duracao_ms=duracao_ms,
                    codigo_http=codigo_http,
                )

    avaliacao_id = registrar_avaliacao_documento(
        documento_id=documento.documento.documento_id,
        documento_hash=documento_hash,
        perfis_compativeis=[
            p.value for p in avaliacao.perfis_compativeis
        ],
        niveis_compativeis=[
            n.value for n in avaliacao.niveis_compativeis
        ],
        perfil_recomendado=(
            avaliacao.perfil_recomendado.value
            if avaliacao.perfil_recomendado else None
        ),
        nivel_recomendado=(
            avaliacao.nivel_recomendado.value
            if avaliacao.nivel_recomendado else None
        ),
        justificativa=avaliacao.justificativa,
        evidencias=avaliacao.evidencias,
        status=avaliacao.status,
        modelo_avaliador=avaliacao.modelo_avaliador,
        versao_avaliador=VERSAO_AVALIADOR,
    )

    return avaliacao_id, avaliacao
