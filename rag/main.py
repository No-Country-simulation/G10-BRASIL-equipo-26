"""NovaMente: API local de teste de Quiz e persistência SQLite.

Copiar para <repositorio>/rag/main.py e executar de rag:
    python -m uvicorn main:app --reload

Uso local/de desenvolvimento: ainda não inclui autenticação para produção.
"""
import json
import os
import tempfile
import sys
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

RAG_DIR = Path(__file__).resolve().parent
REPO_DIR = RAG_DIR.parent
sys.path.insert(0, str(REPO_DIR))
sys.path.insert(0, str(RAG_DIR / "pipeline"))
load_dotenv(RAG_DIR / ".env")
sys.path.insert(0, str(RAG_DIR))

import database as db  # noqa: E402

app = FastAPI(title="NovaMente — API de teste", version="0.3.0")


class IniciarRodada(BaseModel):
    geracao_id: str
    usuario_id: str = Field(min_length=1)
    sessao_id: str = Field(min_length=1)


class Responder(BaseModel):
    geracao_id: str
    usuario_id: str = Field(min_length=1)
    sessao_id: str = Field(min_length=1)
    rodada_id: str
    questao_indice: int = Field(ge=0)
    alternativa_escolhida: int = Field(ge=0)
    tempo_resposta_segundos: float = Field(default=0, ge=0)


def _geracao(gid: str, usuario: str):
    with db.connection() as con:
        row = con.execute("SELECT usuario_id, formato, pacote_json FROM geracoes WHERE geracao_id=?", (gid,)).fetchone()
    if row is None or row["usuario_id"] != usuario:
        raise HTTPException(404, "Geração não encontrada para este usuário")
    if row["formato"] != "Quiz":
        raise HTTPException(400, "A geração selecionada não é um Quiz")
    pacote = json.loads(row["pacote_json"])
    return pacote["conteudo_adaptado"]["questoes"]


def _publicar_questoes(questoes):
    return [{"questao_indice": i, "enunciado": q["enunciado"],
             "alternativas": q["alternativas"], "assunto": q["classificacao"]["assunto"]}
            for i, q in enumerate(questoes)]


@app.on_event("startup")
def preparar_banco():
    db.init_db()
    db.migrate_respostas()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/quiz")
def listar_quizzes(usuario_id: str = Query(min_length=1)):
    with db.connection() as con:
        rows = con.execute("""SELECT geracao_id, data_hora, perfil, nivel
                              FROM geracoes WHERE formato='Quiz' AND usuario_id=?
                              ORDER BY data_hora DESC LIMIT 30""", (usuario_id,)).fetchall()
    return [dict(r) for r in rows]


@app.get("/quiz/{geracao_id}")
def consultar_quiz(geracao_id: str, usuario_id: str = Query(min_length=1)):
    return {"geracao_id": geracao_id, "questoes": _publicar_questoes(_geracao(geracao_id, usuario_id))}


@app.post("/quiz/rodadas")
def iniciar_rodada(dados: IniciarRodada):
    _geracao(dados.geracao_id, dados.usuario_id)
    rodada_id = str(uuid4())
    # A rodada é registrada no banco e validada em cada resposta.
    with db.connection() as con:
        con.execute("""INSERT INTO eventos_estudo
            (data_hora,geracao_id,usuario_id,sessao_id,tipo_evento,item_indice,detalhes_json)
            VALUES (?,?,?,?,?,?,?)""",
            (db.now(), dados.geracao_id, dados.usuario_id, dados.sessao_id,
             "inicio_rodada", None, json.dumps({"rodada_id": rodada_id})))
    return {"rodada_id": rodada_id, "geracao_id": dados.geracao_id}


@app.post("/quiz/respostas")
def responder(dados: Responder):
    questoes = _geracao(dados.geracao_id, dados.usuario_id)
    if dados.questao_indice >= len(questoes):
        raise HTTPException(422, "Índice de questão inválido")
    q = questoes[dados.questao_indice]
    if dados.alternativa_escolhida >= len(q["alternativas"]):
        raise HTTPException(422, "Alternativa inválida")
    with db.connection() as con:
        eventos = con.execute("""SELECT detalhes_json FROM eventos_estudo
            WHERE geracao_id=? AND usuario_id=? AND sessao_id=? AND tipo_evento='inicio_rodada'""",
            (dados.geracao_id, dados.usuario_id, dados.sessao_id)).fetchall()
    if not any(json.loads(e["detalhes_json"]).get("rodada_id") == dados.rodada_id for e in eventos):
        raise HTTPException(400, "Rodada não registrada")
    acertou = dados.alternativa_escolhida == q["indice_resposta_correta"]
    from types import SimpleNamespace
    resultado = SimpleNamespace(acertou=acertou, assunto=q["classificacao"]["assunto"],
                                subassunto=q["classificacao"].get("subassunto"))
    classificacao = SimpleNamespace(nivel_dificuldade=q["classificacao"]["nivel_dificuldade"])
    try:
        tentativa = db.save_resposta(
            dados.geracao_id, dados.usuario_id, dados.sessao_id, dados.questao_indice,
            dados.alternativa_escolhida, resultado, classificacao,
            dados.tempo_resposta_segundos, dados.rodada_id, q["enunciado"])
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    encerrada = acertou or tentativa == 3
    resposta = {"acertou": acertou, "tentativa_numero": tentativa,
                "tentativas_restantes": 0 if encerrada else 3 - tentativa,
                "questao_encerrada": encerrada}
    if encerrada:
        resposta["indice_resposta_correta"] = q["indice_resposta_correta"]
        resposta["explicacao"] = q["explicacao"]
    return resposta


@app.get("/quiz/{geracao_id}/historico")
def historico(geracao_id: str, usuario_id: str = Query(min_length=1)):
    _geracao(geracao_id, usuario_id)
    with db.connection() as con:
        rows = con.execute("""SELECT data_hora, rodada_id, questao_indice, tentativa_numero,
            alternativa_escolhida, acertou, assunto, assunto_id, questao_referencia_id
            FROM respostas WHERE geracao_id=? AND usuario_id=? ORDER BY resposta_id DESC LIMIT 100""",
            (geracao_id, usuario_id)).fetchall()
    return [dict(r) for r in rows]




# Geração de conteúdo usando os mesmos módulos aprovados em teste_integracao.py.
# Limite local de upload: 20 MiB; somente PDF, TXT e Markdown.
CONSULTAS = {
    "Tutorial": "Explique os conceitos centrais do documento em etapas, com exemplos práticos.",
    "Flashcards": "Identifique conceitos e definições importantes para flashcards de revisão.",
    "Quiz": "Identifique fatos e conceitos para perguntas objetivas com quatro alternativas.",
    "TL;DR": "Resuma os pontos mais importantes e conclusões do documento.",
    "Roteiro": "Organize os conceitos em uma sequência de estudo e atividades.",
    "Resumo": "Apresente uma síntese estruturada dos principais temas do documento.",
}


@app.post("/geracoes", summary="Gerar conteúdo a partir de um documento")
def gerar_conteudo(
    arquivo: UploadFile = File(...),
    perfil: str = Form("Iniciante"),
    nivel: str = Form("basico"),
    formato: str = Form("Quiz"),
    quantidade_itens: int = Form(5, ge=1, le=100),
    usuario_id: str = Form(...),
    sessao_id: str = Form(...),
):
    from backend.app.ingestao import processar_documento
    from persistencia import registrar_geracao
    from pipeline.schemas import PedidoGeracao, Perfil, Formato, Dificuldade, PoliticaTokens, PacoteFinal
    from pipeline.rag_retrieval import indice_documento
    from pipeline.llm_pipeline import gerar_de_contexto
    from pipeline.avaliacao_documento import avaliar_documento, comparar_adequacao
    from pipeline.telemetria_llm import definir_execucao, restaurar_execucao, iniciar_tentativa, finalizar_tentativa

    try:
        perfil_enum = Perfil(perfil)
        formato_enum = Formato(formato)
        Dificuldade(nivel)
    except ValueError as exc:
        raise HTTPException(422, f"Perfil, nível ou formato inválido: {exc}") from exc
    if not usuario_id.strip() or not sessao_id.strip():
        raise HTTPException(422, "Usuário e sessão são obrigatórios")
    extensao = Path(arquivo.filename or "").suffix.lower()
    if extensao not in (".pdf", ".txt", ".md"):
        raise HTTPException(422, "Envie PDF, TXT ou Markdown")
    conteudo = arquivo.file.read(20 * 1024 * 1024 + 1)
    if not conteudo or len(conteudo) > 20 * 1024 * 1024:
        raise HTTPException(413, "Arquivo vazio ou maior que 20 MiB")
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY_BACKUP")):
        raise HTTPException(503, "RAG exige uma chave Gemini configurada em rag/.env")

    caminho = None
    execucao_id = str(uuid4())
    token_execucao = definir_execucao(execucao_id)
    try:
        with tempfile.NamedTemporaryFile(suffix=extensao, delete=False) as temp:
            temp.write(conteudo)
            caminho = Path(temp.name)
        documento = processar_documento(caminho_arquivo=str(caminho), documento_id=str(uuid4()))
        avaliacao_id, avaliacao = avaliar_documento(documento, execucao_id=execucao_id)
        adequacao = comparar_adequacao(avaliacao=avaliacao, perfil_solicitado=perfil_enum,
                                       nivel_solicitado=Dificuldade(nivel))
        pedido = PedidoGeracao(
            documento=documento.documento, perfil=perfil_enum, formato=formato_enum,
            nivel=nivel, quantidade_itens=quantidade_itens,
            politica_tokens=PoliticaTokens(permitir_avaliacao_llm=True,
                max_tokens_avaliacao_por_resposta=3000,
                max_tokens_avaliacao_total=3000, max_avaliacoes_llm=1),
        )
        chamadas_ids, token_tentativa = iniciar_tentativa()
        try:
            with indice_documento(documento) as indice:
                contexto = indice.recuperar(pedido=pedido, consulta=CONSULTAS[formato])
                resultado = gerar_de_contexto(contexto)
                pacote = PacoteFinal.model_validate(resultado.pacote.model_dump())
                geracao_id = registrar_geracao(resultado, usuario_id=usuario_id,
                                              sessao_id=sessao_id, avaliacao_id=avaliacao_id)
                db.associar_telemetria_geracao(geracao_id=geracao_id,
                    chamadas_ids=chamadas_ids, execucao_id=execucao_id)
        finally:
            finalizar_tentativa(token_tentativa)
        resposta = {
            "geracao_id": geracao_id, "formato": formato, "perfil": perfil,
            "nivel_solicitado": nivel, "avaliacao_id": avaliacao_id,
            "adequacao": {"divergencia": adequacao.divergencia, "mensagem": adequacao.mensagem},
            "duracao_ms": resultado.duracao_ms,
        }
        if formato_enum == Formato.QUIZ:
            # Nunca expor o gabarito no endpoint de geração.
            resposta["questoes"] = _publicar_questoes(_geracao(geracao_id, usuario_id))
        else:
            resposta["conteudo"] = pacote.model_dump(mode="json")["conteudo_adaptado"]
        return resposta
    except HTTPException:
        raise
    except Exception as exc:
        # Não divulgar detalhes de chaves, prompts ou stack traces ao cliente.
        import logging
        logging.getLogger("novamente.api").exception("Falha na geração")
        raise HTTPException(500, "Falha na geração; consulte o terminal do servidor") from exc
    finally:
        restaurar_execucao(token_execucao)
        if caminho is not None:
            caminho.unlink(missing_ok=True)


HTML = """<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>NovaMente — Quiz local</title>
<style>body{font:16px system-ui;max-width:850px;margin:35px auto;padding:0 16px;background:#f7f9fc;color:#1d2939}
section{background:white;padding:20px;margin:15px 0;border:1px solid #dde3ea;border-radius:12px}
button,select{padding:10px;margin:5px;border-radius:7px;border:1px solid #aab5c3;cursor:pointer}
button:hover{background:#dce9ff}pre{white-space:pre-wrap;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%;font-size:13px}
th,td{border-bottom:1px solid #ddd;padding:7px;text-align:left}small{color:#667085}</style>
<h1>NovaMente — Teste local do Quiz</h1><p><small id="identificacao"></small></p>
<section><h3>Gerar conteúdo de um documento</h3>
<form id="formGeracao"><label>Documento: <input type="file" name="arquivo" accept=".pdf,.txt,.md" required></label>
<label>Perfil: <select name="perfil"><option>Iniciante</option><option>Jr/Pleno</option><option>Tech Lead</option><option>Gestor</option></select></label>
<label>Nível: <select name="nivel"><option value="basico">Básico</option><option value="intermediario">Intermediário</option><option value="avancado">Avançado</option></select></label>
<label>Formato: <select name="formato"><option>Quiz</option><option>Tutorial</option><option>Flashcards</option><option>TL;DR</option><option>Roteiro</option><option>Resumo</option></select></label>
<label>Itens: <input type="number" name="quantidade_itens" value="5" min="1" max="100" style="width:65px"></label>
<button type="submit" id="gerarBtn">Gerar</button></form>
<p id="statusGeracao"></p><pre id="saidaGeracao"></pre></section><p><small>Gabarito oculto até acertar ou esgotar três tentativas. Use somente localmente.</small></p>
<section><label>Quiz salvo: <select id="quiz"></select></label><button onclick="carregar()">Carregar</button>
<button onclick="novaRodada()">Iniciar nova rodada</button><p id="rodada"></p></section>
<section><label>Questão: <select id="questao" onchange="mostrarQuestao()"></select></label><h3 id="enunciado"></h3>
<div id="alternativas"></div><p id="feedback"></p></section>
<section><h3>Histórico no SQLite</h3><button onclick="historico()">Atualizar histórico</button><div id="tabela"></div></section>
<p><a href="/docs">Documentação dos endpoints (Swagger)</a></p>
<script>
let perguntas=[],rodadaId=null;
// Identificação anônima por navegador e por sessão (não equivale a autenticação).
function obterOuCriar(storage,chave){let id=storage.getItem(chave);if(!id){id=crypto.randomUUID();storage.setItem(chave,id)}return id}
const usuarioId=obterOuCriar(localStorage,'novamente_usuario_id');
const sessaoId=obterOuCriar(sessionStorage,'novamente_sessao_id');
document.getElementById('identificacao').textContent='Usuário anônimo: '+usuarioId+' | Sessão: '+sessaoId;
function comUsuario(url){return url+(url.includes('?')?'&':'?')+'usuario_id='+encodeURIComponent(usuarioId)}
async function req(url,opts){let r=await fetch(url,opts),j=await r.json();if(!r.ok)throw Error(JSON.stringify(j));return j}
function post(obj){return {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(obj)}}
function gid(){return document.getElementById('quiz').value}
async function listar(){try{let a=await req(comUsuario('/quiz'));document.getElementById('quiz').innerHTML=a.map(x=>`<option value="${x.geracao_id}">${x.data_hora} — ${x.geracao_id.slice(0,8)}</option>`).join('');if(a.length)await carregar();else document.getElementById('rodada').textContent='Nenhum Quiz encontrado para este navegador. Quizzes antigos de teste_local permanecem no banco.'}catch(e){alert(e.message)}}
async function carregar(){try{let d=await req(comUsuario('/quiz/'+gid()));perguntas=d.questoes;rodadaId=null;document.getElementById('rodada').textContent='Clique em Iniciar nova rodada';document.getElementById('questao').innerHTML=perguntas.map((q,i)=>`<option value="${i}">Questão ${i+1}</option>`).join('');mostrarQuestao();await historico()}catch(e){alert(e.message)}}
function mostrarQuestao(){let i=+document.getElementById('questao').value,q=perguntas[i];if(!q)return;document.getElementById('enunciado').textContent=q.enunciado;let el=document.getElementById('alternativas');el.replaceChildren();q.alternativas.forEach((a,j)=>{let b=document.createElement('button');b.textContent=(j+1)+'. '+a;b.onclick=()=>responder(i,j);el.appendChild(b)});document.getElementById('feedback').textContent=''}
async function novaRodada(){try{let d=await req('/quiz/rodadas',post({geracao_id:gid(),usuario_id:usuarioId,sessao_id:sessaoId}));rodadaId=d.rodada_id;document.getElementById('rodada').textContent='Rodada: '+rodadaId;mostrarQuestao();await historico()}catch(e){alert(e.message)}}
async function responder(i,j){if(!rodadaId){alert('Inicie uma rodada primeiro');return}try{let d=await req('/quiz/respostas',post({geracao_id:gid(),usuario_id:usuarioId,sessao_id:sessaoId,rodada_id:rodadaId,questao_indice:i,alternativa_escolhida:j}));document.getElementById('feedback').textContent=(d.acertou?'Acertou!':'Errou.')+' Tentativa '+d.tentativa_numero+'. Restantes: '+d.tentativas_restantes+(d.questao_encerrada?' | Correta: '+(d.indice_resposta_correta+1)+' — '+d.explicacao:'');await historico()}catch(e){alert(e.message)}}
async function historico(){if(!gid())return;try{let a=await req(comUsuario('/quiz/'+gid()+'/historico'));let cols=['data_hora','rodada_id','questao_indice','tentativa_numero','alternativa_escolhida','acertou','assunto_id'];let t=document.createElement('table'),h=document.createElement('tr');cols.forEach(c=>{let th=document.createElement('th');th.textContent=c;h.appendChild(th)});t.appendChild(h);a.forEach(r=>{let tr=document.createElement('tr');cols.forEach(c=>{let td=document.createElement('td');td.textContent=String(r[c]??'');tr.appendChild(td)});t.appendChild(tr)});document.getElementById('tabela').replaceChildren(t)}catch(e){alert(e.message)}}
document.getElementById('formGeracao').addEventListener('submit',async e=>{
 e.preventDefault();const btn=document.getElementById('gerarBtn'),status=document.getElementById('statusGeracao'),saida=document.getElementById('saidaGeracao');
 btn.disabled=true;status.textContent='Processando documento e gerando conteúdo. Aguarde...';saida.textContent='';
 try{const form=new FormData(e.target);form.set('usuario_id',usuarioId);form.set('sessao_id',sessaoId);const r=await fetch('/geracoes',{method:'POST',body:form});const j=await r.json();
 if(!r.ok)throw Error(JSON.stringify(j));status.textContent='Geração concluída: '+j.geracao_id;
 saida.textContent=JSON.stringify(j,null,2);
 if(j.formato==='Quiz'){await listar();document.getElementById('quiz').value=j.geracao_id;await carregar();}
 }catch(err){status.textContent='Erro: '+err.message}finally{btn.disabled=false}
});
listar();
</script></html>"""


@app.get("/", response_class=HTMLResponse)
def interface():
    return HTML
