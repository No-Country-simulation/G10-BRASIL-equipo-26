"""Leitura e extração de documentos multi-formato para o pipeline de RAG (Fase 2.1)."""

import logging
import re
from pathlib import Path
import pdfplumber

from schemas import DocumentoEntrada, PaginaExtraida, DocumentoExtraido

logger = logging.getLogger(__name__)
FORMATOS_SUPORTADOS = {".pdf", ".md", ".txt"}

def limpar_texto(texto: str) -> str:
    linhas_limpas = []
    for linha in texto.splitlines():
        linha_normalizada = re.sub(r"[^\S\n]+", " ", linha).strip()
        linhas_limpas.append(linha_normalizada)
    
    texto_limpo = "\n".join(linhas_limpas)
    texto_limpo = re.sub(r"\n{3,}", "\n\n", texto_limpo)
    return texto_limpo.strip()

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

def _extrair_pdf(caminho: Path, documento_id: str) -> list[PaginaExtraida]:
    paginas = []
    with pdfplumber.open(caminho) as pdf:
        for numero, pagina in enumerate(pdf.pages, start=1):
            texto = pagina.extract_text() or ""
            
            tabelas_md = []
            tabelas_brutas = pagina.extract_tables()
            for tabela in tabelas_brutas:
                if tabela:
                    tabelas_md.append("\n\n### Tabela Extraída:")
                    for linha in tabela:
                        linha_limpa = [str(celula).replace('\n', ' ') if celula else " " for celula in linha]
                        tabelas_md.append("| " + " | ".join(linha_limpa) + " |")
            
            texto_completo = texto + "\n".join(tabelas_md)
            texto_limpo = limpar_texto(texto_completo)
            
            if texto_limpo:
                paginas.append(
                    PaginaExtraida(
                        documento_id=documento_id,
                        pagina=numero,
                        texto=texto_limpo
                    )
                )
    return paginas

def _extrair_texto_simples(caminho: Path, documento_id: str) -> list[PaginaExtraida]:
    texto = caminho.read_text(encoding="utf-8-sig")
    texto_limpo = limpar_texto(texto)
    
    if not texto_limpo:
        return []
        
    return [PaginaExtraida(documento_id=documento_id, pagina=1, texto=texto_limpo)]

def processar_documento(caminho_arquivo: str, documento_id: str | None = None) -> DocumentoExtraido:
    caminho, extensao = _validar_arquivo(caminho_arquivo)
    doc_id = documento_id or caminho.stem
    tipo_arquivo = extensao[1:]

    info_documento = DocumentoEntrada(
        documento_id=doc_id,
        nome_arquivo=caminho.name,
        tipo_arquivo=tipo_arquivo,
    )

    try:
        if extensao == ".pdf":
            paginas_extraidas = _extrair_pdf(caminho, doc_id)
        else:
            paginas_extraidas = _extrair_texto_simples(caminho, doc_id)
    except Exception:
        logger.exception("Erro ao processar %s", caminho.name)
        raise

    if not paginas_extraidas:
        raise ValueError("Nenhum conteúdo textual válido foi extraído.")

    logger.info("Arquivo processado: %s | Páginas válidas: %d", caminho.name, len(paginas_extraidas))
    
    return DocumentoExtraido(documento=info_documento, paginas=paginas_extraidas)

    """Leitura e extração de documentos multi-formato para o pipeline de RAG (Fase 2.1)."""

import logging
import re
from pathlib import Path
import pdfplumber

from schemas import DocumentoEntrada, PaginaExtraida, DocumentoExtraido

logger = logging.getLogger(__name__)
FORMATOS_SUPORTADOS = {".pdf", ".md", ".txt"}

def limpar_texto(texto: str) -> str:
    linhas_limpas = []
    for linha in texto.splitlines():
        linha_normalizada = re.sub(r"[^\S\n]+", " ", linha).strip()
        linhas_limpas.append(linha_normalizada)
    
    texto_limpo = "\n".join(linhas_limpas)
    texto_limpo = re.sub(r"\n{3,}", "\n\n", texto_limpo)
    return texto_limpo.strip()

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

def _extrair_pdf(caminho: Path, documento_id: str) -> list[PaginaExtraida]:
    paginas = []
    with pdfplumber.open(caminho) as pdf:
        for numero, pagina in enumerate(pdf.pages, start=1):
            texto = pagina.extract_text() or ""
            
            tabelas_md = []
            tabelas_brutas = pagina.extract_tables()
            for tabela in tabelas_brutas:
                if tabela:
                    tabelas_md.append("\n\n### Tabela Extraída:")
                    for linha in tabela:
                        linha_limpa = [str(celula).replace('\n', ' ') if celula else " " for celula in linha]
                        tabelas_md.append("| " + " | ".join(linha_limpa) + " |")
            
            texto_completo = texto + "\n".join(tabelas_md)
            texto_limpo = limpar_texto(texto_completo)
            
            if texto_limpo:
                paginas.append(
                    PaginaExtraida(
                        documento_id=documento_id,
                        pagina=numero,
                        texto=texto_limpo
                    )
                )
    return paginas

def _extrair_texto_simples(caminho: Path, documento_id: str) -> list[PaginaExtraida]:
    texto = caminho.read_text(encoding="utf-8-sig")
    texto_limpo = limpar_texto(texto)
    
    if not texto_limpo:
        return []
        
    return [PaginaExtraida(documento_id=documento_id, pagina=1, texto=texto_limpo)]

def processar_documento(caminho_arquivo: str, documento_id: str | None = None) -> DocumentoExtraido:
    caminho, extensao = _validar_arquivo(caminho_arquivo)
    doc_id = documento_id or caminho.stem
    tipo_arquivo = extensao[1:]

    info_documento = DocumentoEntrada(
        documento_id=doc_id,
        nome_arquivo=caminho.name,
        tipo_arquivo=tipo_arquivo,
    )

    try:
        if extensao == ".pdf":
            paginas_extraidas = _extrair_pdf(caminho, doc_id)
        else:
            paginas_extraidas = _extrair_texto_simples(caminho, doc_id)
    except Exception:
        logger.exception("Erro ao processar %s", caminho.name)
        raise

    if not paginas_extraidas:
        raise ValueError("Nenhum conteúdo textual válido foi extraído.")

    logger.info("Arquivo processado: %s | Páginas válidas: %d", caminho.name, len(paginas_extraidas))
    
    return DocumentoExtraido(documento=info_documento, paginas=paginas_extraidas)