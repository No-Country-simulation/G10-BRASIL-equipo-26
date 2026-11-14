"""SQLite local: eventos e respostas. Sem coleta de nome/email/IP."""
import csv
import hashlib
import unicodedata
import re
import io
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(os.environ.get('NOVAMENTE_DB_PATH', str(Path(__file__).resolve().parent / 'novamente.db')))

def now():
    return datetime.now(timezone.utc).isoformat()

@contextmanager
def connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")

    try:
        yield con
        con.commit()

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()

def init_db():
    with connection() as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS geracoes (
          geracao_id TEXT PRIMARY KEY, data_hora TEXT NOT NULL,
          usuario_id TEXT NOT NULL, sessao_id TEXT NOT NULL,
          documento_id TEXT, perfil TEXT NOT NULL, formato TEXT NOT NULL,
          nivel TEXT, quantidade_itens INTEGER NOT NULL,
          tempo_estimado_estudo_minutos REAL, ancoragem_fonte_score REAL,
          modelo_llm TEXT, duracao_geracao_ms REAL, pacote_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS respostas (
          resposta_id INTEGER PRIMARY KEY AUTOINCREMENT,
          data_hora TEXT NOT NULL, geracao_id TEXT NOT NULL REFERENCES geracoes(geracao_id),
          usuario_id TEXT NOT NULL, sessao_id TEXT NOT NULL,
          questao_indice INTEGER NOT NULL, questao_id TEXT NOT NULL,
          assunto TEXT, subassunto TEXT, dificuldade TEXT,
          alternativa_escolhida INTEGER NOT NULL, acertou INTEGER NOT NULL,
          tempo_resposta_segundos REAL, tentativa_numero INTEGER NOT NULL,
          UNIQUE(geracao_id, usuario_id, questao_indice, tentativa_numero)
        );
        CREATE TABLE IF NOT EXISTS eventos_estudo (
          evento_id INTEGER PRIMARY KEY AUTOINCREMENT, data_hora TEXT NOT NULL,
          geracao_id TEXT NOT NULL REFERENCES geracoes(geracao_id),
          usuario_id TEXT NOT NULL, sessao_id TEXT NOT NULL,
          tipo_evento TEXT NOT NULL, item_indice INTEGER,
          detalhes_json TEXT NOT NULL DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS avaliacoes_documento (
            avaliacao_id TEXT PRIMARY KEY,
            documento_id TEXT NOT NULL,
            documento_hash TEXT NOT NULL,
            data_avaliacao TEXT NOT NULL,
            perfis_compativeis TEXT NOT NULL DEFAULT '[]',
            niveis_compativeis TEXT NOT NULL DEFAULT '[]',
            perfil_recomendado TEXT,
            nivel_recomendado TEXT,
            justificativa TEXT,
            evidencias_json TEXT NOT NULL DEFAULT '[]',
            status TEXT NOT NULL
                CHECK (status IN ('avaliado', 'inconclusivo', 'indisponivel')),
            modelo_avaliador TEXT,
            versao_avaliador TEXT NOT NULL DEFAULT '1'
        );

        CREATE INDEX IF NOT EXISTS idx_avaliacoes_documento_hash
        ON avaliacoes_documento(documento_hash, versao_avaliador);

        CREATE TABLE IF NOT EXISTS telemetria_api (
            chamada_id TEXT PRIMARY KEY,
            execucao_id TEXT NOT NULL,
            geracao_id TEXT REFERENCES geracoes(geracao_id),
            documento_id TEXT,
            data_hora TEXT NOT NULL,
            provedor TEXT NOT NULL,
            modelo TEXT NOT NULL,
            operacao TEXT NOT NULL,
            tokens_entrada INTEGER,
            tokens_saida INTEGER,
            tokens_totais INTEGER,
            duracao_ms REAL,
            status TEXT NOT NULL CHECK (status IN ('sucesso', 'erro')),
            codigo_http INTEGER
        );

        CREATE INDEX IF NOT EXISTS idx_telemetria_execucao
        ON telemetria_api(execucao_id);

        CREATE INDEX IF NOT EXISTS idx_telemetria_geracao
        ON telemetria_api(geracao_id);

        CREATE INDEX IF NOT EXISTS idx_respostas_data ON respostas(data_hora);
        CREATE INDEX IF NOT EXISTS idx_eventos_tipo ON eventos_estudo(tipo_evento);
        ''')
    migrate_geracoes()
    migrate_avaliacao_geracoes()

def migrate_geracoes():
    """Remove nicho de bancos legados sem recriar tabelas ou alterar FKs."""
    with connection() as con:
        cols = {r['name'] for r in con.execute('PRAGMA table_info(geracoes)')}
        if 'nicho' not in cols:
            return
        if sqlite3.sqlite_version_info < (3, 35, 0):
            raise RuntimeError('Migração requer SQLite 3.35 ou superior.')
        # Backup consistente usando a API do SQLite (inclusive em modo WAL).
        backup_path = DB_PATH.with_name(DB_PATH.name + '.antes_remover_nicho.bak')
        if backup_path.exists():
            raise FileExistsError(f'Backup já existe; migração interrompida: {backup_path}')
        with sqlite3.connect(backup_path) as backup:
            con.backup(backup)
        try:
            con.execute('ALTER TABLE geracoes DROP COLUMN nicho')
            problemas = con.execute('PRAGMA foreign_key_check').fetchall()
            if problemas:
                raise RuntimeError(f'Integridade referencial comprometida: {problemas}')
        except Exception:
            con.rollback()
            raise

def migrate_respostas():
    with connection() as con:
        cols={x['name'] for x in con.execute('PRAGMA table_info(respostas)')}
        if 'rodada_id' in cols: return
        con.executescript('''
        CREATE TABLE respostas_nova (
          resposta_id INTEGER PRIMARY KEY AUTOINCREMENT,
          data_hora TEXT NOT NULL, geracao_id TEXT NOT NULL REFERENCES geracoes(geracao_id),
          usuario_id TEXT NOT NULL, sessao_id TEXT NOT NULL,
          questao_indice INTEGER NOT NULL, questao_id TEXT NOT NULL,
          assunto TEXT, subassunto TEXT, dificuldade TEXT,
          alternativa_escolhida INTEGER NOT NULL, acertou INTEGER NOT NULL,
          tempo_resposta_segundos REAL, tentativa_numero INTEGER NOT NULL,
          rodada_id TEXT NOT NULL, assunto_id TEXT, questao_referencia_id TEXT,
          UNIQUE(geracao_id,usuario_id,questao_indice,rodada_id,tentativa_numero)
        );
        INSERT INTO respostas_nova (resposta_id,data_hora,geracao_id,usuario_id,sessao_id,questao_indice,questao_id,assunto,subassunto,dificuldade,alternativa_escolhida,acertou,tempo_resposta_segundos,tentativa_numero,rodada_id)
        SELECT resposta_id,data_hora,geracao_id,usuario_id,sessao_id,questao_indice,questao_id,assunto,subassunto,dificuldade,alternativa_escolhida,acertou,tempo_resposta_segundos,tentativa_numero,'legado_' || resposta_id FROM respostas;
        DROP TABLE respostas;
        ALTER TABLE respostas_nova RENAME TO respostas;
        CREATE INDEX IF NOT EXISTS idx_respostas_data ON respostas(data_hora);
        CREATE INDEX IF NOT EXISTS idx_respostas_assunto ON respostas(assunto_id);
        CREATE INDEX IF NOT EXISTS idx_respostas_questao_ref ON respostas(questao_referencia_id);
        ''')

def save_geracao(gid, user, session, pacote, duracao_ms, avaliacao_id=None):
    m = pacote.metadados
    conteudo = pacote.conteudo_adaptado
    itens = getattr(conteudo, 'questoes', None) or getattr(conteudo, 'itens', None) or getattr(conteudo, 'secoes', None) or getattr(conteudo, 'passos', None) or getattr(conteudo, 'etapas', None) or []
    with connection() as con:
        con.execute('''INSERT INTO geracoes (geracao_id,data_hora,usuario_id,sessao_id,documento_id,perfil,formato,nivel,quantidade_itens,tempo_estimado_estudo_minutos,ancoragem_fonte_score,modelo_llm,duracao_geracao_ms,pacote_json, avaliacao_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
            gid, now(), user, session, m.documento_id, m.perfil.value, m.formato.value,
            m.nivel.value if hasattr(m.nivel,'value') else str(m.nivel), len(itens),
            m.tempo_estimado_estudo_minutos, pacote.avaliacao_qualidade.ancoragem_fonte_score,
            m.modelo_llm, duracao_ms, pacote.model_dump_json(), avaliacao_id,),)

def get_pacote_json(gid):
    with connection() as con:
        row = con.execute('SELECT pacote_json FROM geracoes WHERE geracao_id=?', (gid,)).fetchone()
    return json.loads(row['pacote_json']) if row else None

def stable_id(prefix, text):
    text=unicodedata.normalize('NFKD',text or '').encode('ascii','ignore').decode().casefold()
    text=' '.join(text.split())
    return prefix+'_'+hashlib.sha256(text.encode()).hexdigest()[:20]

def save_resposta(gid,user,session,indice,alternativa,resultado,classificacao,segundos,rodada_id,questao_texto):
    with connection() as con:
        con.execute('BEGIN IMMEDIATE')
        ger=con.execute('SELECT usuario_id FROM geracoes WHERE geracao_id=?',(gid,)).fetchone()
        if ger is None or ger['usuario_id']!=user: raise ValueError('Usuário incompatível com a geração.')
        anterior=con.execute('SELECT acertou FROM respostas WHERE geracao_id=? AND usuario_id=? AND questao_indice=? AND rodada_id=? ORDER BY tentativa_numero',(gid,user,indice,rodada_id)).fetchall()
        if len(anterior)>=3 or any(x['acertou'] for x in anterior): raise ValueError('Rodada encerrada.')
        tentativa=len(anterior)+1
        con.execute('''INSERT INTO respostas (data_hora,geracao_id,usuario_id,sessao_id,questao_indice,questao_id,assunto,subassunto,dificuldade,alternativa_escolhida,acertou,tempo_resposta_segundos,tentativa_numero,rodada_id,assunto_id,questao_referencia_id)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(now(),gid,user,session,indice,f'{gid}:q{indice+1}',resultado.assunto,resultado.subassunto,classificacao.nivel_dificuldade.value if hasattr(classificacao.nivel_dificuldade,'value') else str(classificacao.nivel_dificuldade),alternativa,int(resultado.acertou),segundos,tentativa,rodada_id,stable_id('assunto',resultado.assunto),stable_id('questao',questao_texto)))
    return tentativa

def save_event(gid, user, session, tipo, indice=None):
    with connection() as con:
        con.execute('INSERT INTO eventos_estudo (data_hora,geracao_id,usuario_id,sessao_id,tipo_evento,item_indice) VALUES (?,?,?,?,?,?)',(now(),gid,user,session,tipo,indice))

def summary():
    with connection() as con:
        total=con.execute('SELECT COUNT(*) n FROM geracoes').fetchone()['n']
        r=con.execute('SELECT COUNT(*) n, ROUND(AVG(acertou)*100,2) acerto_pct, ROUND(AVG(tempo_resposta_segundos),2) tempo_medio_s FROM respostas').fetchone()
        formatos=[dict(x) for x in con.execute('SELECT formato, COUNT(*) quantidade FROM geracoes GROUP BY formato ORDER BY quantidade DESC')]
        assuntos=[dict(x) for x in con.execute('SELECT assunto,COUNT(*) respostas,ROUND(AVG(acertou)*100,2) acerto_pct,ROUND(AVG(tempo_resposta_segundos),2) tempo_medio_s FROM respostas GROUP BY assunto')]
    return {'geracoes':total,'respostas':r['n'],'taxa_acerto_pct':r['acerto_pct'],'tempo_medio_resposta_segundos':r['tempo_medio_s'],'formatos':formatos,'assuntos':assuntos,'observacao':'Dados simulados, produzidos por interações reais com conteúdo fixo; não representam desempenho em conteúdo gerado por RAG/LLM.'}

TABLES={'geracoes':['geracao_id','data_hora','usuario_id','sessao_id','documento_id','perfil','formato','nivel','quantidade_itens','tempo_estimado_estudo_minutos','ancoragem_fonte_score','modelo_llm','duracao_geracao_ms'], 'respostas':None,'eventos_estudo':None}
def export_csv(table):
    if table not in TABLES: raise ValueError('Tabela inválida')
    with connection() as con:
        columns=TABLES[table] or [r['name'] for r in con.execute(f'PRAGMA table_info({table})') if r['name']!='detalhes_json']
        query='SELECT '+','.join(columns)+' FROM '+table+' ORDER BY data_hora'
        rows=con.execute(query).fetchall()
    out=io.StringIO();writer=csv.writer(out);writer.writerow(columns);writer.writerows([[row[c] for c in columns] for row in rows]);return out.getvalue()


# ============================================================
# AVALIAÇÃO DE ADEQUAÇÃO DO DOCUMENTO
# ============================================================

def save_avaliacao_documento(
    avaliacao_id,
    documento_id,
    documento_hash,
    perfis_compativeis,
    niveis_compativeis,
    perfil_recomendado=None,
    nivel_recomendado=None,
    justificativa=None,
    evidencias=None,
    status="inconclusivo",
    modelo_avaliador=None,
    versao_avaliador="1",
):
    if status not in {"avaliado", "inconclusivo", "indisponivel"}:
        raise ValueError("Status de avaliação inválido.")

    with connection() as con:
        con.execute(
            """
            INSERT INTO avaliacoes_documento (
                avaliacao_id,
                documento_id,
                documento_hash,
                data_avaliacao,
                perfis_compativeis,
                niveis_compativeis,
                perfil_recomendado,
                nivel_recomendado,
                justificativa,
                evidencias_json,
                status,
                modelo_avaliador,
                versao_avaliador
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                avaliacao_id,
                documento_id,
                documento_hash,
                now(),
                json.dumps(perfis_compativeis, ensure_ascii=False),
                json.dumps(niveis_compativeis, ensure_ascii=False),
                perfil_recomendado,
                nivel_recomendado,
                justificativa,
                json.dumps(evidencias or [], ensure_ascii=False),
                status,
                modelo_avaliador,
                versao_avaliador,
            ),
        )


def get_avaliacao_documento(documento_hash, versao_avaliador="1"):
    with connection() as con:
        row = con.execute(
            """
            SELECT *
            FROM avaliacoes_documento
            WHERE documento_hash = ?
              AND versao_avaliador = ?
            ORDER BY data_avaliacao DESC, rowid DESC
            LIMIT 1
            """,
            (documento_hash, versao_avaliador),
        ).fetchone()

    if row is None:
        return None

    resultado = dict(row)
    resultado["perfis_compativeis"] = json.loads(
        resultado["perfis_compativeis"]
    )
    resultado["niveis_compativeis"] = json.loads(
        resultado["niveis_compativeis"]
    )
    resultado["evidencias_json"] = json.loads(
        resultado["evidencias_json"]
    )

    return resultado


# ============================================================
# TELEMETRIA DAS CHAMADAS ÀS APIS
# ============================================================

def save_telemetria_api(
    chamada_id,
    execucao_id,
    provedor,
    modelo,
    operacao,
    status,
    geracao_id=None,
    documento_id=None,
    tokens_entrada=None,
    tokens_saida=None,
    tokens_totais=None,
    duracao_ms=None,
    codigo_http=None,
):
    if status not in {"sucesso", "erro"}:
        raise ValueError("Status de telemetria inválido.")

    with connection() as con:
        con.execute(
            """
            INSERT INTO telemetria_api (
                chamada_id,
                execucao_id,
                geracao_id,
                documento_id,
                data_hora,
                provedor,
                modelo,
                operacao,
                tokens_entrada,
                tokens_saida,
                tokens_totais,
                duracao_ms,
                status,
                codigo_http
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                chamada_id,
                execucao_id,
                geracao_id,
                documento_id,
                now(),
                provedor,
                modelo,
                operacao,
                tokens_entrada,
                tokens_saida,
                tokens_totais,
                duracao_ms,
                status,
                codigo_http,
            ),
        )


def get_telemetria_execucao(execucao_id):
    with connection() as con:
        rows = con.execute(
            """
            SELECT *
            FROM telemetria_api
            WHERE execucao_id = ?
            ORDER BY data_hora, rowid
            """,
            (execucao_id,),
        ).fetchall()

    return [dict(row) for row in rows]

def migrate_avaliacao_geracoes():
    """Adiciona a referência à avaliação sem alterar registros antigos."""
    with connection() as con:
        colunas = {
            row["name"]
            for row in con.execute("PRAGMA table_info(geracoes)")
        }

        if "avaliacao_id" not in colunas:
            con.execute("""
                ALTER TABLE geracoes
                ADD COLUMN avaliacao_id TEXT
                REFERENCES avaliacoes_documento(avaliacao_id)
            """)


def associar_telemetria_geracao(
    geracao_id,
    chamadas_ids,
    execucao_id,
):
    """Associa chamadas de API a uma geração já salva."""

    if not chamadas_ids:
        return 0

    if len(chamadas_ids) != len(set(chamadas_ids)):
        raise ValueError("Identificadores de chamadas duplicados.")

    placeholders = ",".join("?" for _ in chamadas_ids)

    with connection() as con:
        geracao = con.execute(
            """
            SELECT 1
            FROM geracoes
            WHERE geracao_id = ?
            """,
            (geracao_id,),
        ).fetchone()

        if geracao is None:
            raise ValueError("Geração não encontrada.")

        cursor = con.execute(
            f"""
            UPDATE telemetria_api
            SET geracao_id = ?
            WHERE execucao_id = ?
              AND geracao_id IS NULL
              AND chamada_id IN ({placeholders})
            """,
            (geracao_id, execucao_id, *chamadas_ids),
        )

        if cursor.rowcount != len(chamadas_ids):
            raise ValueError(
                "Nem todas as chamadas foram associadas à geração."
            )

        return cursor.rowcount
