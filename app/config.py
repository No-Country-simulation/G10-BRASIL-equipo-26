"""Configurações centralizadas do frontend Streamlit (MentorIA Tech)."""

import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
REPO_DIR = APP_DIR.parent
ASSETS_DIR = APP_DIR / "assets"
SAMPLE_PDF_PATH = REPO_DIR / "rag" / "Machine_Learning.pdf"

DEFAULT_API_URL = "http://127.0.0.1:8000"
TIMEOUT_HEALTH = (3, 5)
TIMEOUT_PADRAO = (5, 20)
TIMEOUT_GERACAO = (5, 300)

MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20 MiB conforme contrato v0.3
EXTENSOES_SUPORTADAS = ("pdf", "txt", "md")

QTD_ITENS_MIN = 1
QTD_ITENS_MAX = 20
QTD_ITENS_PADRAO = 5

PERFIS: dict[str, str] = {
    "Iniciante / Transição": "Iniciante",
    "Desenvolvedor Jr/Pleno": "Jr/Pleno",
    "Líder Técnico / Arquiteto": "Tech Lead",
    "Gestor / Executivo": "Gestor",
}

NIVEIS: dict[str, str] = {
    "Básico (Didático)": "basico",
    "Intermediário": "intermediario",
    "Avançado": "avancado",
}

FORMATOS: dict[str, str] = {
    "Quiz Interativo": "Quiz",
    "Guia Passo a Passo (Tutorial)": "Tutorial",
    "Flashcards de Memorização": "Flashcards",
    "Resumo Executivo (TL;DR)": "TL;DR",
    "Roteiro de Aula / Vídeo": "Roteiro",
    "Resumo Estruturado": "Resumo",
}

MIME_POR_EXTENSAO: dict[str, str] = {
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".md": "text/markdown",
}


def obter_config(chave: str, padrao: str = "") -> str:
    """Lê configuração de variável de ambiente ou Streamlit Secrets sem falhar."""
    valor_env = os.getenv(chave, "").strip()
    if valor_env:
        return valor_env

    try:
        import streamlit as st

        if hasattr(st, "secrets") and chave in st.secrets:
            valor_secret = str(st.secrets[chave]).strip()
            if valor_secret:
                return valor_secret
    except Exception:
        pass

    return padrao


def obter_api_base_url() -> str:
    """Retorna a URL base da API FastAPI sem barra final."""
    return obter_config("MENTORIA_API_URL", DEFAULT_API_URL).rstrip("/")


def obter_bucket_artefatos() -> str:
    """Retorna o nome oficial do bucket OCI para artefatos."""
    return obter_config("OCI_BUCKET_ARTIFACTS", "mentoria-tech-artifacts")
