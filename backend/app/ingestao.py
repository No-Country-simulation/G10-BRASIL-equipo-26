"""Leitura e extração de documentos para o pipeline de RAG."""

import logging
import re
from pathlib import Path

from pypdf import PdfReader
from rag.pipeline.schemas import DocumentoEntrada, DocumentoExtraido, PaginaExtraida


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
    documento_id: str,
) -> PaginaExtraida | None:
    texto_limpo = limpar_texto(texto)

    if not texto_limpo:
        logger.warning(
            "Página ou documento sem texto: %s (página %d)",
            caminho.name,
            pagina,
        )
        return None

    return PaginaExtraida(
        documento_id=documento_id,
        pagina=pagina,
        texto=texto_limpo,
    )

def processar_documento(
    caminho_arquivo: str,
    documento_id: str | None = None,
) -> DocumentoExtraido:
    caminho, extensao = _validar_arquivo(caminho_arquivo)
    identificador = caminho.stem if documento_id is None else documento_id

    try:
        partes_extraidas = (
            _extrair_pdf(caminho)
            if extensao == ".pdf"
            else _extrair_texto_simples(caminho)
        )
    except Exception:
        logger.exception("Erro ao processar %s", caminho.name)
        raise

    paginas = [
        documento
        for pagina, texto in partes_extraidas
        if (documento := _criar_documento(
            texto,
            pagina,
            caminho,
            identificador,
        )) is not None
    ]

    if not paginas:
        raise ValueError("Nenhum conteúdo textual válido foi extraído.")

    documento = DocumentoExtraido(
        documento=DocumentoEntrada(
            documento_id=identificador,
            nome_arquivo=caminho.name,
            tipo_arquivo=extensao[1:],
        ),
        paginas=paginas,
    )

    logger.info(
        "Arquivo processado: %s | Páginas com texto: %d",
        caminho.name,
        len(documento.paginas),
    )
    return documento