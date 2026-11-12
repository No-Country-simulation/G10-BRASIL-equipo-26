
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "pipeline"), str(ROOT)]

from schemas import (
    ContextoRAG,
    PedidoGeracao,
    DocumentoEntrada,
    TrechoRecuperado,
    PoliticaTokens,
    Perfil,
    Formato,
)
from llm_pipeline import gerar_de_contexto

caminho = ROOT / "resultados_teste_local" / "quiz.json"

pacote = json.loads(
    caminho.read_text(encoding="utf-8")
)

conteudo = pacote["conteudo_adaptado"]
documento_id = pacote["metadados"]["documento_id"]

ids = {}

for questao in conteudo["questoes"]:
    for fonte in questao["fontes"]:
        for cid in fonte["chunk_ids"]:
            ids[cid] = fonte["paginas"][0]

pedido = PedidoGeracao(
    documento=DocumentoEntrada(
        documento_id=documento_id,
        nome_arquivo="Machine_Learning.pdf",
    ),
    perfil=Perfil.INICIANTE,
    formato=Formato.QUIZ,
    nivel="basico",
    quantidade_itens=len(conteudo["questoes"]),
    politica_tokens=PoliticaTokens(
        permitir_avaliacao_llm=False,
    ),
)

contexto = ContextoRAG(
    pedido=pedido,
    trechos=[
        TrechoRecuperado(
            chunk_id=cid,
            documento_id=documento_id,
            texto="Trecho simulado para teste.",
            paginas=[pagina],
            posicao=i + 1,
        )
        for i, (cid, pagina) in enumerate(ids.items())
    ],
)

chamadas = []

def chamar_gemini(system, user, max_output_tokens=None):
    chamadas.append("gemini")
    raise RuntimeError("Falha simulada do Gemini")

def chamar_groq(system, user, max_output_tokens=None):
    chamadas.append("groq")
    return (
        json.dumps(conteudo, ensure_ascii=False),
        "groq-mock",
    )

resultado = gerar_de_contexto(
    contexto,
    provedores=[chamar_gemini, chamar_groq],
)

assert chamadas == ["gemini", "groq"], chamadas

assert (
    resultado.pacote.metadados.modelo_llm
    == "groq-mock"
)

assert (
    resultado.pacote.conteudo_adaptado.formato
    == "Quiz"
)

print(
    "APROVADO: falha simulada do Gemini "
    "acionou o Groq."
)
print(
    "Este teste não verifica a API Groq real."
)
