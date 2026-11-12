
import os
import sys
import json
import sqlite3
import tempfile
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

ROOT = Path(__file__).resolve().parent
QUIZ = ROOT / "resultados_teste_local" / "quiz.json"

quiz = json.loads(QUIZ.read_text(encoding="utf-8"))
questao = quiz["conteudo_adaptado"]["questoes"][0]
meta = quiz["metadados"]

correta = questao["indice_resposta_correta"]
errada = next(
    i for i in range(len(questao["alternativas"]))
    if i != correta
)

with tempfile.TemporaryDirectory() as pasta:
    os.environ["NOVAMENTE_DB_PATH"] = str(
        Path(pasta) / "teste.db"
    )

    sys.path.insert(0, str(ROOT))
    import database as db

    assert Path(db.DB_PATH).resolve() == Path(
        os.environ["NOVAMENTE_DB_PATH"]
    ).resolve(), "O database.py não usa o banco temporário."

    db.init_db()
    db.migrate_respostas()

    gid = "teste-" + uuid4().hex
    usuario = "usuario_teste"
    sessao = "sessao_teste"

    dados = {
        "geracao_id": gid,
        "data_hora": db.now(),
        "usuario_id": usuario,
        "sessao_id": sessao,
        "documento_id": meta["documento_id"],
        "perfil": meta["perfil"],
        "formato": "Quiz",
        "nicho": "Geral",
        "nivel": meta["nivel"],
        "quantidade_itens": len(
            quiz["conteudo_adaptado"]["questoes"]
        ),
        "pacote_json": json.dumps(
            quiz, ensure_ascii=False
        ),
    }

    with db.connection() as con:
        colunas = {
            r["name"]: r
            for r in con.execute(
                "PRAGMA table_info(geracoes)"
            )
        }

        # Usa apenas as colunas existentes no banco real.
        dados = {
            k: v for k, v in dados.items()
            if k in colunas
        }

        obrigatorias = {
            k for k, info in colunas.items()
            if info["notnull"]
            and info["dflt_value"] is None
            and not info["pk"]
        }

        faltando = obrigatorias - dados.keys()
        assert not faltando, (
            f"Colunas obrigatórias desconhecidas: {faltando}"
        )

        nomes = list(dados)
        placeholders = ",".join("?" for _ in nomes)
        sql = (
            f"INSERT INTO geracoes "
            f"({','.join(nomes)}) "
            f"VALUES ({placeholders})"
        )

        con.execute(sql, list(dados.values()))

    cl = questao["classificacao"]
    classificacao = SimpleNamespace(
        nivel_dificuldade=cl["nivel_dificuldade"]
    )

    def responder(indice, rodada):
        resultado = SimpleNamespace(
            acertou=indice == correta,
            assunto=cl["assunto"],
            subassunto=cl.get("subassunto"),
        )

        return db.save_resposta(
            gid,
            usuario,
            sessao,
            0,
            indice,
            resultado,
            classificacao,
            2.0,
            rodada,
            questao["enunciado"],
        )

    def deve_bloquear(indice, rodada):
        try:
            responder(indice, rodada)
        except ValueError:
            return
        raise AssertionError(
            f"Resposta indevida aceita na rodada {rodada}"
        )

    assert responder(errada, "dia1") == 1
    assert responder(errada, "dia1") == 2
    assert responder(correta, "dia1") == 3
    deve_bloquear(errada, "dia1")

    assert responder(correta, "dia2") == 1
    deve_bloquear(errada, "dia2")

    assert responder(errada, "dia3") == 1

    with sqlite3.connect(db.DB_PATH) as con:
        linhas = con.execute("""
            SELECT rodada_id, tentativa_numero,
                   acertou, assunto_id,
                   questao_referencia_id
            FROM respostas
            ORDER BY resposta_id
        """).fetchall()

        assert len(linhas) == 5
        assert [r[1] for r in linhas] == [1, 2, 3, 1, 1]
        assert [r[2] for r in linhas] == [0, 0, 1, 1, 0]
        assert len({r[3] for r in linhas}) == 1
        assert len({r[4] for r in linhas}) == 1

    # Recuperação após reabrir a conexão.
    with sqlite3.connect(db.DB_PATH) as con:
        registro = con.execute(
            "SELECT pacote_json FROM geracoes "
            "WHERE geracao_id = ?",
            (gid,),
        ).fetchone()

        recuperado = json.loads(registro[0])

        assert (
            recuperado["conteudo_adaptado"]
            ["questoes"][0]["enunciado"]
            == questao["enunciado"]
        )

        total = con.execute(
            "SELECT COUNT(*) FROM respostas "
            "WHERE geracao_id = ?",
            (gid,),
        ).fetchone()[0]

        assert total == 5

    print(
        "APROVADO: tentativas, bloqueios, "
        "novas rodadas e persistência SQLite."
    )
# Fechar explicitamente as conexões abertas pelo teste.
    import gc

    try:
        con.close()
    except Exception:
        pass

    gc.collect()