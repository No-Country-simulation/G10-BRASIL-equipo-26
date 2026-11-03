"""Extrator provisório baseado em pypdf, usado apenas nos testes.
A equipe substituirá este adaptador pela ingestão definitiva.
"""
from pathlib import Path
from pypdf import PdfReader
from schemas import DocumentoEntrada, DocumentoExtraido, PaginaExtraida

def extrair_pdf(caminho):
    if not caminho.is_file():
        raise FileNotFoundError(
            f"PDF não encontrado: {caminho}"
        )

    leitor = PdfReader(str(caminho))
    documento_id = caminho.stem

    info = DocumentoEntrada(
        documento_id=documento_id,
        nome_arquivo=caminho.name,
        tipo_arquivo="pdf",
    )

    paginas = []

    for numero, pagina in enumerate(leitor.pages, start=1):
        texto = (pagina.extract_text() or "").strip()

        if texto:
            paginas.append(
                PaginaExtraida(
                    documento_id=documento_id,
                    pagina=numero,
                    texto=texto,
                )
            )

    if not paginas:
        raise RuntimeError(
            "Nenhuma página com texto extraível foi encontrada."
        )

    return DocumentoExtraido(
        documento=info,
        paginas=paginas,
    ), len(leitor.pages)


