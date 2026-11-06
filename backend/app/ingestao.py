"""Leitura e extração de documentos para o pipeline de RAG.

O módulo possui uma única responsabilidade externa: transformar um arquivo
PDF, Markdown ou texto bruto em documentos LangChain prontos para consumo.
As funções privadas separam as etapas internas desse fluxo.
"""

import logging
import re
from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader


logger = logging.getLogger(__name__)
FORMATOS_SUPORTADOS = {".pdf", ".md", ".txt"}

#Responsabilidade: normalizar espaços sem remover a estrutura de parágrafos.
def limpar_texto(texto: str) -> str:
    linhas_limpas = []

    for linha in texto.splitlines():
        linha_normalizada = re.sub(r"[^\S\n]+", " ", linha).strip()
        linhas_limpas.append(linha_normalizada)

    texto_limpo = "\n".join(linhas_limpas)
    texto_limpo = re.sub(r"\n{3,}", "\n\n", texto_limpo)
    return texto_limpo.strip()

#Responsabilidade: validar caminho e formato antes de iniciar a extração.
def _validar_arquivo(caminho_arquivo: str) -> tuple[Path, str]:
    caminho = Path(caminho_arquivo)
    extensao = caminho.suffix.lower()

    if extensao not in FORMATOS_SUPORTADOS:
        raise ValueError(f"Formato não suportado: {extensao or '(sem extensão)'}")

    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    if not caminho.is_file():
        raise ValueError("O caminho informado não é um arquivo.")

    return caminho, extensao

#Responsabilidade: extrair o texto de cada página de um PDF.
def _extrair_pdf(caminho: Path) -> list[tuple[int, str]]:
    leitor = PdfReader(str(caminho))
    return [
        (numero, pagina.extract_text() or "")
        for numero, pagina in enumerate(leitor.pages, start=1)
    ]

#Responsabilidade: ler Markdown ou TXT como um único documento lógico.
def _extrair_texto_simples(caminho: Path) -> list[tuple[int, str]]:
    return [(1, caminho.read_text(encoding="utf-8-sig"))]

#Responsabilidade: criar um documento LangChain a partir do texto extraído.
def _criar_documento(
    texto: str,
    pagina: int,
    caminho: Path,
    extensao: str,
    documento_id: str | None,
) -> Document | None:
    texto_limpo = limpar_texto(texto)

    if not texto_limpo:
        logger.warning(
            "Página ou documento sem texto: %s (página %d)",
            caminho.name,
            pagina,
        )
        return None

    metadata = {
        "nome_arquivo": caminho.name,
        "tipo_arquivo": extensao[1:],
        "caminho_origem": str(caminho.resolve()),
        "pagina_origem": pagina if extensao == ".pdf" else None,
    }

    if documento_id is not None:
        metadata["documento_id"] = documento_id

    return Document(page_content=texto_limpo, metadata=metadata)

# Responsabilidade: coordenar a validação, extração, limpeza e retorno de documentos.
def processar_documento(
    caminho_arquivo: str,
    documento_id: str | None = None,
) -> list[Document]:
    caminho, extensao = _validar_arquivo(caminho_arquivo)

    try:
        partes_extraidas = (
            _extrair_pdf(caminho)
            if extensao == ".pdf"
            else _extrair_texto_simples(caminho)
        )
    except Exception:
        logger.exception("Erro ao processar %s", caminho.name)
        raise

    documentos = [
        documento
        for pagina, texto in partes_extraidas
        if (documento := _criar_documento(
            texto,
            pagina,
            caminho,
            extensao,
            documento_id,
        )) is not None
    ]

    if not documentos:
        raise ValueError("Nenhum conteúdo textual válido foi extraído.")

    logger.info(
        "Arquivo processado: %s | Documentos: %d",
        caminho.name,
        len(documentos),
    )
    return documentos