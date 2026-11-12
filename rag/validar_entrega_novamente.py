
"""Validação de formatos e SQLite, somente leitura."""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SAIDA = ROOT / "resultados_teste_local"
DB = ROOT / "novamente.db"
falhas = []

def verificar(nome, condicao, detalhe=""):
    status = "OK" if condicao else "FALHOU"
    print(f"{status} | {nome} {detalhe}")
    if not condicao:
        falhas.append(nome)

formatos = {
    "tutorial": "Tutorial",
    "flashcards": "Flashcards",
    "quiz": "Quiz",
    "tldr": "TL;DR",
    "roteiro": "Roteiro",
    "resumo": "Resumo",
}

print("\n=== PRODUTOS GERADOS ===")

for arquivo, formato in formatos.items():
    caminho = SAIDA / f"{arquivo}.json"

    if not caminho.exists():
        verificar(f"{arquivo}.json existe", False)
        continue

    try:
        pacote = json.loads(caminho.read_text(encoding="utf-8"))
        meta = pacote["metadados"]
        conteudo = pacote["conteudo_adaptado"]

        verificar(
            f"{formato}: formato",
            meta["formato"] == formato
            and conteudo["formato"] == formato,
        )

        verificar(
            f"{formato}: modelo registrado",
            bool(meta.get("modelo_llm")),
        )

        chave = {
            "Tutorial": "passos",
            "Flashcards": "itens",
            "Quiz": "questoes",
            "Roteiro": "etapas",
            "Resumo": "secoes",
        }.get(formato)

        if chave:
            verificar(
                f"{formato}: conteúdo",
                bool(conteudo.get(chave)),
            )
        else:
            verificar(
                "TL;DR: conteúdo",
                bool(conteudo.get("resumo"))
                and bool(conteudo.get("pontos_chave")),
            )

        if formato == "Quiz":
            questoes = conteudo.get("questoes", [])

            verificar(
                "Quiz: alternativas e índices",
                bool(questoes)
                and all(
                    len(q["alternativas"]) == 4
                    and 0 <= q["indice_resposta_correta"] < 4
                    for q in questoes
                ),
            )

            houve_adaptacao = (
                meta.get("perfil_solicitado") != meta.get("perfil_efetivo")
                or meta.get("nivel_solicitado") != meta.get("nivel_efetivo")
            )

            verificar(
                "Quiz: aviso de adaptação",
                not houve_adaptacao
                or bool(meta.get("motivo_adaptacao")),
            )

    except Exception as exc:
        verificar(f"{formato}: JSON válido", False, repr(exc))

print("\n=== SQLITE ===")

if not DB.exists():
    verificar("Banco novamente.db encontrado", False)
else:
    try:
        con = sqlite3.connect(
            f"file:{DB.as_posix()}?mode=ro",
            uri=True,
        )
        con.row_factory = sqlite3.Row

        tabelas = {
            r[0]
            for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }

        for tabela in ("geracoes", "respostas", "eventos_estudo"):
            verificar(f"Tabela {tabela}", tabela in tabelas)

        if "geracoes" in tabelas:
            registros = con.execute(
                "SELECT formato, COUNT(*) AS total "
                "FROM geracoes GROUP BY formato"
            ).fetchall()

            print(
                "Gerações por formato:",
                {r["formato"]: r["total"] for r in registros},
            )

            verificar(
                "Seis formatos no SQLite",
                {r["formato"] for r in registros}
                >= set(formatos.values()),
            )

            for r in con.execute(
                "SELECT geracao_id, formato, pacote_json "
                "FROM geracoes ORDER BY data_hora DESC LIMIT 10"
            ):
                try:
                    pacote = json.loads(r["pacote_json"])
                    verificar(
                        "Recuperação " + str(r["geracao_id"])[:8],
                        pacote["metadados"]["formato"] == r["formato"],
                    )
                except Exception as exc:
                    verificar("Recuperação de pacote", False, repr(exc))

        if "respostas" in tabelas:
            colunas = {
                r["name"]
                for r in con.execute("PRAGMA table_info(respostas)")
            }

            verificar(
                "Colunas de histórico",
                {"rodada_id", "assunto_id", "questao_referencia_id"}
                <= colunas,
            )

            total = con.execute(
                "SELECT COUNT(*) FROM respostas"
            ).fetchone()[0]

            print("Respostas registradas:", total)

        con.close()

    except Exception as exc:
        verificar("Leitura do SQLite", False, repr(exc))

print("\n=== RESULTADO ===")
print("Falhas:", len(falhas), falhas)
raise SystemExit(bool(falhas))
