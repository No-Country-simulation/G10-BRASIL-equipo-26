
"""Teste manual dos seis formatos com PDF real, RAG Gemini/Groq, Pydantic e SQLite.

Executar da raiz do repositório:
    python .\rag\teste_integracao.py caminho\arquivo.pdf

Ou dentro da pasta rag:
    python teste_integracao.py ".\\Machine_Learning.pdf"

Não modifica os módulos do pipeline nem executa o benchmark.
Requer rag/database.py e rag/persistencia.py.
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# CONFIGURAÇÃO DOS CAMINHOS
# ============================================================

RAIZ_RAG = Path(__file__).resolve().parent
RAIZ_REPOSITORIO = RAIZ_RAG.parent

sys.path.insert(0, str(RAIZ_REPOSITORIO))
sys.path.insert(0, str(RAIZ_RAG))
sys.path.insert(0, str(RAIZ_RAG / "pipeline"))

load_dotenv(RAIZ_RAG / ".env")


# ============================================================
# IMPORTAÇÕES DO PROJETO
# ============================================================

from database import init_db, migrate_respostas
from persistencia import registrar_geracao
from backend.app.ingestao import processar_documento

from pipeline.schemas import (
    PedidoGeracao,
    Perfil,
    Formato,
    PacoteFinal,
    PoliticaTokens,
)

from pipeline.rag_retrieval import indice_documento
from pipeline.llm_pipeline import gerar_de_contexto


# ============================================================
# CONSULTAS PARA OS SEIS PRODUTOS
# ============================================================

CONSULTAS = {
    Formato.TUTORIAL: (
        "Explique os conceitos centrais do documento em etapas, "
        "com exemplos práticos."
    ),
    Formato.FLASHCARDS: (
        "Identifique conceitos e definições importantes "
        "para flashcards de revisão."
    ),
    Formato.QUIZ: (
        "Identifique fatos e conceitos para perguntas objetivas "
        "com quatro alternativas."
    ),
    Formato.TLDR: (
        "Resuma os pontos mais importantes e conclusões do documento."
    ),
    Formato.ROTEIRO: (
        "Organize os conceitos em uma sequência de estudo e atividades."
    ),
    Formato.RESUMO: (
        "Apresente uma síntese estruturada dos principais temas "
        "do documento."
    ),
}


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='Teste integrado ingestão + RAG + LLM + Pydantic + SQLite.')

    parser.add_argument('pdf', type=Path, help='Caminho para PDF, Markdown ou TXT')

    args = parser.parse_args()

    pdf = args.pdf.resolve()

    if not pdf.is_file():
        parser.error(f'PDF não encontrado: {pdf}')

    if not os.getenv('GEMINI_API_KEY'):
        parser.error('Configure GEMINI_API_KEY no ambiente ou em rag/.env')

    if not pdf.is_file():
        parser.error(f"PDF não encontrado: {pdf}")

    if not (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GEMINI_API_KEY_BACKUP")
        or os.getenv("GROQ_API_KEY")
    ):
        parser.error(
            "Configure ao menos uma chave Gemini ou Groq "
            "no ambiente ou em rag/.env"
        )

    # --------------------------------------------------------
    # INICIALIZAÇÃO DO SQLITE
    # --------------------------------------------------------

    # Faça backup de novamente.db antes de executar
    # caso existam dados antigos importantes.

    init_db()
    migrate_respostas()

    print("SQLite inicializado.", flush=True)

    # --------------------------------------------------------
    # PROCESSAMENTO DO PDF
    # --------------------------------------------------------

    documento = processar_documento(
        caminho_arquivo=str(pdf),
        documento_id="teste_integracao_001",
    )

    print(
        f"PDF: {pdf.name} | "
        f"páginas com texto: {len(documento.paginas)}",
        flush=True,
    )

    # --------------------------------------------------------
    # DIRETÓRIO DE SAÍDA
    # --------------------------------------------------------

    saida = RAIZ_RAG / "resultados_teste_local"
    saida.mkdir(parents=True, exist_ok=True)

    falhas = []
    sucessos = 0

    # --------------------------------------------------------
    # INDEXAÇÃO E GERAÇÃO DOS SEIS FORMATOS
    # --------------------------------------------------------

    with indice_documento(documento) as indice:

        print(
            f"Chunks indexados: {indice.quantidade_chunks}",
            flush=True,
        )

        for formato, consulta in CONSULTAS.items():

            print(
                f"\nGerando {formato.value}...",
                flush=True,
            )

            try:

                # --------------------------------------------
                # PEDIDO DE GERAÇÃO
                # --------------------------------------------

                pedido = PedidoGeracao(
                    documento=documento.documento,
                    perfil=Perfil.ARQUITETO,
                    formato=formato,
                    nivel="avancado",
                    quantidade_itens=5,
                    politica_tokens=PoliticaTokens(
                        permitir_avaliacao_llm=True,
                        max_tokens_avaliacao_por_resposta=3000,
                        max_tokens_avaliacao_total=3000,
                        max_avaliacoes_llm=1,
                    ),
                )

                # --------------------------------------------
                # RECUPERAÇÃO RAG
                # --------------------------------------------

                contexto = indice.recuperar(
                    pedido=pedido,
                    consulta=consulta,
                )

                # --------------------------------------------
                # GERAÇÃO GEMINI / GROQ
                # --------------------------------------------

                resultado = gerar_de_contexto(contexto)

                # --------------------------------------------
                # VALIDAÇÃO PYDANTIC
                # --------------------------------------------

                pacote = PacoteFinal.model_validate(
                    resultado.pacote.model_dump()
                )

                # --------------------------------------------
                # PERSISTÊNCIA SQLITE
                # --------------------------------------------

                geracao_id = registrar_geracao(resultado)

                # --------------------------------------------
                # SALVAMENTO JSON
                # --------------------------------------------

                nome = (
                    "tldr"
                    if formato == Formato.TLDR
                    else formato.value.lower()
                )

                destino = saida / f"{nome}.json"

                destino.write_text(
                    pacote.model_dump_json(indent=2),
                    encoding="utf-8",
                )

                # --------------------------------------------
                # CONTAGEM DE SUCESSOS
                # --------------------------------------------

                sucessos += 1

                print(
                    f"OK | {resultado.provedor} | "
                    f"{resultado.duracao_ms / 1000:.1f}s | "
                    f"geracao_id={geracao_id} | {destino}",
                    flush=True,
                )

                if resultado.erros_anteriores:
                    print(
                        f"  Falhas anteriores: "
                        f"{resultado.erros_anteriores}",
                        flush=True,
                    )

            except Exception as exc:

                falhas.append(formato.value)

                print(
                    f"ERRO ({formato.value}): "
                    f"{type(exc).__name__}: {exc}",
                    flush=True,
                )

    # --------------------------------------------------------
    # RESULTADO FINAL
    # --------------------------------------------------------

    print("\n" + "=" * 55)
    print("RESULTADO FINAL DA INTEGRAÇÃO")
    print("=" * 55)

    print(
        f"Produtos gerados: {sucessos}/{len(CONSULTAS)}",
        flush=True,
    )

    print(
        f"Falhas: {len(falhas)}",
        flush=True,
    )

    if falhas:
        print(
            "Formatos com falha: " + ", ".join(falhas),
            flush=True,
        )
        raise SystemExit(1)

    print(
        "\nAPROVADO: seis produtos gerados, "
        "validados e registrados no SQLite.",
        flush=True,
    )


if __name__ == "__main__":
    main()
