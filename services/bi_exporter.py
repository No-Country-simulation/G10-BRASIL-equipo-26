"""Exportador de dados para Power BI via arquivos CSV.

Responsabilidade:
  - Lê as tabelas do banco SQLite local (novamente.db).
  - Exporta cada tabela como arquivo CSV para data/bi_exports/.
  - Os CSVs podem ser conectados diretamente no Power BI Desktop
    via "Obter Dados → Texto/CSV".
  - Opcionalmente envia os CSVs para o bucket mentoria-tech-observability na OCI.

Tabelas exportadas:
  - geracoes       → histórico de gerações de conteúdo
  - respostas      → respostas de quizzes dos usuários
  - eventos_estudo → eventos de navegação e estudo
  - feedbacks      → avaliações (estrelas + comentário) — se existir

Uso:
    from services.bi_exporter import exportar_tudo
    caminhos = exportar_tudo()
    print(caminhos)  # {'geracoes': 'data/bi_exports/geracoes.csv', ...}
"""

import csv
import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
_env_path = Path(__file__).parent.parent / "rag" / ".env"
if not _env_path.exists():
    _env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=False)

# Caminho do banco e da pasta de exportação
_DB_PATH = Path(
    os.environ.get("NOVAMENTE_DB_PATH",
                   str(Path(__file__).parent.parent / "rag" / "novamente.db"))
)
_PASTA_EXPORT = Path(__file__).parent.parent / "data" / "bi_exports"

# Tabelas a exportar (nome → arquivo CSV de saída)
_TABELAS = {
    "geracoes": "geracoes.csv",
    "respostas": "respostas.csv",
    "eventos_estudo": "eventos_estudo.csv",
    "feedbacks": "feedbacks.csv",  # exportado apenas se a tabela existir
}

# Colunas com JSON embutido — serão removidas para facilitar leitura no Power BI
_COLUNAS_JSON = {"pacote_json", "detalhes_json"}


def _tabela_existe(con: sqlite3.Connection, nome: str) -> bool:
    """Verifica se uma tabela existe no banco SQLite."""
    cursor = con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (nome,)
    )
    return cursor.fetchone() is not None


def _exportar_tabela(con: sqlite3.Connection, tabela: str, destino: Path) -> bool:
    """Exporta uma tabela para CSV. Retorna False se a tabela não existir."""
    if not _tabela_existe(con, tabela):
        logger.info("Tabela '%s' não existe — pulando exportação.", tabela)
        return False

    cursor = con.execute(f"SELECT * FROM {tabela}")  # noqa: S608
    colunas = [desc[0] for desc in cursor.description]
    colunas_exportar = [c for c in colunas if c not in _COLUNAS_JSON]
    indices_exportar = [i for i, c in enumerate(colunas) if c not in _COLUNAS_JSON]

    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "w", newline="", encoding="utf-8-sig") as f:
        # utf-8-sig = UTF-8 com BOM, necessário para Excel/Power BI reconhecer acentos
        writer = csv.writer(f)
        writer.writerow(colunas_exportar)
        for linha in cursor:
            writer.writerow([linha[i] for i in indices_exportar])

    logger.info("Exportado: %s → %s", tabela, destino)
    return True


def exportar_tudo(pasta_destino: Path | None = None) -> dict[str, str]:
    """Exporta todas as tabelas do banco para CSV.

    Args:
        pasta_destino: Pasta onde os CSVs serão salvos.
                       Padrão: data/bi_exports/ na raiz do projeto.

    Returns:
        Dicionário {nome_tabela: caminho_csv} para as tabelas exportadas com sucesso.
    """
    destino = pasta_destino or _PASTA_EXPORT

    if not _DB_PATH.exists():
        logger.warning(
            "Banco de dados não encontrado em %s. "
            "Execute o pipeline ao menos uma vez para gerar o banco.",
            _DB_PATH,
        )
        return {}

    exportados: dict[str, str] = {}
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")

    with sqlite3.connect(_DB_PATH) as con:
        for tabela, arquivo_csv in _TABELAS.items():
            # Adiciona data ao nome do arquivo para controle de versão
            nome_arquivo = arquivo_csv.replace(".csv", f"_{ts}.csv")
            caminho_csv = destino / nome_arquivo
            if _exportar_tabela(con, tabela, caminho_csv):
                exportados[tabela] = str(caminho_csv)

    if exportados:
        logger.info(
            "Exportação concluída: %d tabela(s) em %s", len(exportados), destino
        )
    else:
        logger.warning("Nenhuma tabela exportada. Verifique se o banco possui dados.")

    return exportados


def exportar_tabela_unica(tabela: str, pasta_destino: Path | None = None) -> str | None:
    """Exporta apenas uma tabela específica.

    Args:
        tabela: Nome da tabela a exportar.
        pasta_destino: Pasta de destino (padrão: data/bi_exports/).

    Returns:
        Caminho do CSV gerado, ou None se a tabela não existir.
    """
    destino = pasta_destino or _PASTA_EXPORT
    arquivo_csv = _TABELAS.get(tabela, f"{tabela}.csv")
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    nome_arquivo = arquivo_csv.replace(".csv", f"_{ts}.csv")
    caminho_csv = destino / nome_arquivo

    if not _DB_PATH.exists():
        logger.warning("Banco não encontrado em %s.", _DB_PATH)
        return None

    with sqlite3.connect(_DB_PATH) as con:
        sucesso = _exportar_tabela(con, tabela, caminho_csv)

    return str(caminho_csv) if sucesso else None
