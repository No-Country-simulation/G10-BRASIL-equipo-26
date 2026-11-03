"""Teste manual dos seis formatos com PDF real, RAG Gemini e validação Pydantic.

Executar da raiz do repositório: python .\rag\teste_integracao.py caminho\arquivo.pdf
Não modifica os módulos do pipeline nem executa o benchmark.
"""
import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

RAIZ_RAG = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ_RAG / 'pipeline'))
sys.path.insert(0, str(RAIZ_RAG))
load_dotenv(RAIZ_RAG / '.env')

from extrator_temporario.extrair_pdf_teste import extrair_pdf
from schemas import PedidoGeracao, Perfil, Formato, Nicho, PacoteFinal
from rag_retrieval import indice_documento
from llm_pipeline import gerar_de_contexto

CONSULTAS = {
    Formato.TUTORIAL: 'Explique os conceitos centrais do documento em etapas, com exemplos práticos.',
    Formato.FLASHCARDS: 'Identifique conceitos e definições importantes para flashcards de revisão.',
    Formato.QUIZ: 'Identifique fatos e conceitos para perguntas objetivas com quatro alternativas.',
    Formato.TLDR: 'Resuma os pontos mais importantes e conclusões do documento.',
    Formato.ROTEIRO: 'Organize os conceitos em uma sequência de estudo e atividades.',
    Formato.RESUMO: 'Apresente uma síntese estruturada dos principais temas do documento.',
}


def main():
    parser = argparse.ArgumentParser(description='Teste integrado RAG + LLM + Pydantic.')
    parser.add_argument('pdf', type=Path, help='Caminho para PDF com texto selecionável')
    args = parser.parse_args()
    pdf = args.pdf.resolve()
    if not pdf.is_file():
        parser.error(f'PDF não encontrado: {pdf}')
    if not os.getenv('GEMINI_API_KEY'):
        parser.error('Configure GEMINI_API_KEY no ambiente ou em rag/.env')

    documento, total_paginas = extrair_pdf(pdf)
    print(f'PDF: {pdf.name} | páginas: {total_paginas} | com texto: {len(documento.paginas)}', flush=True)
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
                nome = 'tldr' if formato == Formato.TLDR else formato.value.lower()
                destino = saida / f'{nome}.json'
                destino.write_text(pacote.model_dump_json(indent=2), encoding='utf-8')
                print(f'OK | {resultado.provedor} | {resultado.duracao_ms / 1000:.1f}s | {destino}', flush=True)
                if resultado.erros_anteriores:
                    print(f'  Falhas anteriores: {resultado.erros_anteriores}', flush=True)
            except Exception as exc:
                falhas.append(formato.value)
                print(f'ERRO ({formato.value}): {type(exc).__name__}: {exc}', flush=True)
    print(f'\nFinalizado. {len(CONSULTAS)-len(falhas)}/{len(CONSULTAS)} formatos gerados.', flush=True)
    if falhas:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
