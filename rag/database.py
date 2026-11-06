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
    con.execute('PRAGMA foreign_keys=ON')
    try:
        yield con
        con.commit()
    finally:
        con.close()

def init_db():
    with connection() as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS geracoes (
          geracao_id TEXT PRIMARY KEY, data_hora TEXT NOT NULL,
          usuario_id TEXT NOT NULL, sessao_id TEXT NOT NULL,
          documento_id TEXT, perfil TEXT NOT NULL, formato TEXT NOT NULL,
          nicho TEXT NOT NULL, nivel TEXT, quantidade_itens INTEGER NOT NULL,
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
        CREATE INDEX IF NOT EXISTS idx_respostas_data ON respostas(data_hora);
        CREATE INDEX IF NOT EXISTS idx_eventos_tipo ON eventos_estudo(tipo_evento);
        ''')

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

def save_geracao(gid, user, session, pacote, duracao_ms):
    m = pacote.metadados
    conteudo = pacote.conteudo_adaptado
    itens = getattr(conteudo, 'questoes', None) or getattr(conteudo, 'itens', None) or getattr(conteudo, 'secoes', None) or getattr(conteudo, 'passos', None) or getattr(conteudo, 'etapas', None) or []
    with connection() as con:
        con.execute('''INSERT INTO geracoes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
            gid, now(), user, session, m.documento_id, m.perfil.value, m.formato.value,
            m.nicho.value, m.nivel.value if hasattr(m.nivel,'value') else str(m.nivel), len(itens),
            m.tempo_estimado_estudo_minutos, pacote.avaliacao_qualidade.ancoragem_fonte_score,
            m.modelo_llm, duracao_ms, pacote.model_dump_json()))

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

TABLES={'geracoes':['geracao_id','data_hora','usuario_id','sessao_id','documento_id','perfil','formato','nicho','nivel','quantidade_itens','tempo_estimado_estudo_minutos','ancoragem_fonte_score','modelo_llm','duracao_geracao_ms'], 'respostas':None,'eventos_estudo':None}
def export_csv(table):
    if table not in TABLES: raise ValueError('Tabela inválida')
    with connection() as con:
        columns=TABLES[table] or [r['name'] for r in con.execute(f'PRAGMA table_info({table})') if r['name']!='detalhes_json']
        query='SELECT '+','.join(columns)+' FROM '+table+' ORDER BY data_hora'
        rows=con.execute(query).fetchall()
    out=io.StringIO();writer=csv.writer(out);writer.writerow(columns);writer.writerows([[row[c] for c in columns] for row in rows]);return out.getvalue()
