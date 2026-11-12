"""Gerenciamento de credenciais para o MentorIA Tech.

Estratégia de leitura (MVP):
  1. Lê variáveis de ambiente do arquivo .env via python-dotenv.
  2. Suporta pool de chaves separadas por vírgula para rotação automática.
  3. USE_OCI_VAULT=false (padrão MVP) — sem chamadas ao OCI Vault.
  4. USE_OCI_VAULT=true  → pós-MVP: lê secrets do OCI Vault (requer Vault criado).

Uso:
    from services.oci_secrets import obter_chave_gemini, obter_chave_groq
    chave = obter_chave_gemini()
"""

import logging
import os
from itertools import cycle
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Carrega o .env do diretório rag/ se existir, senão tenta a raiz
_env_path = Path(__file__).parent.parent / "rag" / ".env"
if not _env_path.exists():
    _env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=False)


def _carregar_pool(env_pool: str, env_single: str) -> list[str]:
    """Carrega uma lista de chaves a partir de variável de pool ou variável simples."""
    pool_raw = os.getenv(env_pool, "").strip()
    if pool_raw:
        chaves = [c.strip() for c in pool_raw.split(",") if c.strip()]
        if chaves:
            logger.info("Pool de chaves carregado de %s: %d chave(s).", env_pool, len(chaves))
            return chaves

    chave_simples = os.getenv(env_single, "").strip()
    if chave_simples:
        logger.info("Chave simples carregada de %s.", env_single)
        return [chave_simples]

    return []


# Pools de chaves — carregados uma vez na inicialização do módulo
_pool_gemini = _carregar_pool("GEMINI_API_KEYS", "GEMINI_API_KEY")
_pool_groq = _carregar_pool("GROQ_API_KEYS", "GROQ_API_KEY")

# Iteradores cíclicos para rotação
_ciclo_gemini = cycle(_pool_gemini) if _pool_gemini else None
_ciclo_groq = cycle(_pool_groq) if _pool_groq else None


def obter_chave_gemini() -> str:
    """Retorna a próxima chave Gemini disponível no pool.

    Raises:
        EnvironmentError: Se nenhuma chave Gemini estiver configurada no .env.
    """
    if _ciclo_gemini is None:
        raise EnvironmentError(
            "Nenhuma chave Gemini encontrada. "
            "Configure GEMINI_API_KEY ou GEMINI_API_KEYS no arquivo .env"
        )
    return next(_ciclo_gemini)


def obter_chave_groq() -> str:
    """Retorna a próxima chave Groq disponível no pool.

    Raises:
        EnvironmentError: Se nenhuma chave Groq estiver configurada no .env.
    """
    if _ciclo_groq is None:
        raise EnvironmentError(
            "Nenhuma chave Groq encontrada. "
            "Configure GROQ_API_KEY ou GROQ_API_KEYS no arquivo .env"
        )
    return next(_ciclo_groq)


def pool_gemini_disponivel() -> bool:
    """Retorna True se há pelo menos uma chave Gemini configurada."""
    return _ciclo_gemini is not None


def pool_groq_disponivel() -> bool:
    """Retorna True se há pelo menos uma chave Groq configurada."""
    return _ciclo_groq is not None
