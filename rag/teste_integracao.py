"""Teste manual dos seis formatos com documento real, RAG Gemini/Groq, Pydantic e SQLite.

Executar da raiz do repositório: python .\rag\teste_integracao.py caminho\arquivo
Não modifica os módulos do pipeline nem executa o benchmark.
Requer rag/database.py e rag/persistencia.py.
"""
import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

RAIZ_RAG = Path(__file__).resolve().parent
RAIZ_PROJETO = RAIZ_RAG.parent
sys.path.insert(0, str(RAIZ_PROJETO / 'backend'))
sys.path.insert(0, str(RAIZ_RAG / 'pipeline'))
sys.path.insert(0, str(RAIZ_RAG))
load_dotenv(RAIZ_RAG / '.env')

from database import init_db, migrate_respostas
from persistencia import registrar_geracao
from backend.app.ingestao import processar_documento
from pipeline.schemas import PedidoGeracao, Perfil, Formato, Nicho, PacoteFinal
from pipeline.rag_retrieval import indice_documento
from pipeline.llm_pipeline import gerar_de_contexto

CONSULTAS = {
    Formato.TUTORIAL: 'Explique os conceitos centrais do documento em etapas, com exemplos práticos.',
    Formato.FLASHCARDS: 'Identifique conceitos e definições importantes para flashcards de revisão.',
    Formato.QUIZ: 'Identifique fatos e conceitos para perguntas objetivas com quatro alternativas.',
    Formato.TLDR: 'Resuma os pontos mais importantes e conclusões do documento.',
    Formato.ROTEIRO: 'Organize os conceitos em uma sequência de estudo e atividades.',
    Formato.RESUMO: 'Apresente uma síntese estruturada dos principais temas do documento.',
}


def main():
    parser = argparse.ArgumentParser(description='Teste integrado ingestão + RAG + LLM + Pydantic + SQLite.')
    parser.add_argument('arquivo', type=Path, help='Caminho para PDF, Markdown ou TXT')
    args = parser.parse_args()
    arquivo = args.arquivo.resolve()
    if not arquivo.is_file():
        parser.error(f'Arquivo não encontrado: {arquivo}')
    if not os.getenv('GEMINI_API_KEY'):
        parser.error('Configure GEMINI_API_KEY no ambiente ou em rag/.env')

    # Cria as tabelas se necessário e aplica a migração existente do banco.
    # Faça backup de novamente.db antes da primeira execução com dados antigos.
    init_db()
    migrate_respostas()
    print('SQLite inicializado.', flush=True)

    documento = processar_documento(str(arquivo), documento_id=arquivo.stem)
    print(
        f'Arquivo: {arquivo.name} | páginas com texto: {len(documento.paginas)}',
        flush=True,
    )
    saida = RAIZ_RAG / 'resultados_teste_local'
    saida.mkdir(exist_ok=True)
    falhas = []

    with indice_documento(documento) as indice:
        print(f'Chunks indexados: {indice.quantidade_chunks}', flush=True)
        for formato, consulta in CONSULTAS.items():
            print(f'\nGerando {formato.value}...', flush=True)
            try:
                pedido = PedidoGeracao(
                    documento=documento.documento,
                    perfil=Perfil.INICIANTE,
                    formato=formato,
                    nicho=Nicho.GERAL,
                    nivel='basico',
                    quantidade_itens=5,
                )
                contexto = indice.recuperar(pedido=pedido, consulta=consulta)
                resultado = gerar_de_contexto(contexto)
                pacote = PacoteFinal.model_validate(resultado.pacote.model_dump())

                # Registra a geração real na tabela geracoes sem alterar seu esquema.
                # O adaptador recebe ResultadoPipeline e persiste resultado.pacote.
                geracao_id = registrar_geracao(resultado)

                nome = 'tldr' if formato == Formato.TLDR else formato.value.lower()
                destino = saida / f'{nome}.json'
                destino.write_text(pacote.model_dump_json(indent=2), encoding='utf-8')
                print(
                    f'OK | {resultado.provedor} | {resultado.duracao_ms / 1000:.1f}s '
                    f'| geracao_id={geracao_id} | {destino}',
                    flush=True,
                )
                if resultado.erros_anteriores:
                    print(f'  Falhas anteriores: {resultado.erros_anteriores}', flush=True)
            except Exception as exc:
                falhas.append(formato.value)
                print(f'ERRO ({formato.value}): {type(exc).__name__}: {exc}', flush=True)

    print(f'\nFinalizado. {len(CONSULTAS)-len(falhas)}/{len(CONSULTAS)} formatos gerados e registrados.', flush=True)
    if falhas:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
