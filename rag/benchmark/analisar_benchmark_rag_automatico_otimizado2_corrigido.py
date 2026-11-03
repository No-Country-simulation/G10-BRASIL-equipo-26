"""
Benchmark multi-PDF para RAG:
- PDFs: pasta ./pdfs/
- Perguntas: ./perguntas_teste.csv
- Saída: ./benchmark_rag_multidocumentos.csv

CSV de perguntas:
pergunta,documento_esperado
"Qual é o objetivo do documento?","manual_oracle.pdf"
"Como funciona o processo descrito?","guia_processos.pdf"

A coluna documento_esperado é opcional. Quando preenchida, permite medir
se o reranker recuperou ao menos um trecho do PDF esperado. Isso é uma
métrica de diagnóstico por documento, não substitui avaliação por trecho
relevante nem avaliação da resposta final do LLM.
"""

import os
import csv
import json
import time
import uuid
import shutil
import tempfile
from pathlib import Path
from statistics import mean
from itertools import product

import pandas as pd
import requests
from pypdf import PdfReader
from dotenv import load_dotenv

from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document


load_dotenv()

# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA_BASE = Path(__file__).resolve().parent
PASTA_PDFS = PASTA_BASE / "pdfs"
PASTA_PERGUNTAS = PASTA_BASE / "perguntas"
PASTA_RESULTADOS = PASTA_BASE / "analise_benchmark" / "voyage"
PDF_ATUAL = None
ARQUIVO_PERGUNTAS = None
ARQUIVO_RESULTADOS = None
ARQUIVO_DETALHES = None
ARQUIVO_AUDITORIA = None

VOYAGE_EMBEDDING_MODEL = "voyage-4"
VOYAGE_RERANKER_MODEL = "rerank-3"

# Os tamanhos continuam em CARACTERES, não em tokens.
CHUNK_SIZES = [500, 1000, 1500, 2000]
OVERLAP_RATIOS = [0.10, 0.20]
K_VALUES = [5, 10, 15]
TOP_N_VALUES = [3, 5]

EMBEDDING_BATCH_SIZE = 64
EMBEDDING_MAX_TOKENS_ESTIMADOS = 5000  # margem adicional contra HTTP 429; lote adaptativo
REQUEST_TIMEOUT = 90
PAUSA_ENTRE_CONFIGURACOES = 1.0


# ============================================================
# VOYAGE AI — ADAPTADORES DA API E CONTROLE DO PLANO GRATUITO
# Mantém as interfaces embed_documents, embed_query e rerank.
# ============================================================

from collections import deque

class VoyageFreeRateLimiter:
    """Limites conservadores para conta gratuita sem cartão: 3 RPM e 10k TPM.

    A estimativa de tokens é usada apenas para limitar chamadas à API,
    nunca para calcular as métricas do benchmark.
    """
    def __init__(self):
        self.chamadas = deque()
        self.limite_tokens = 9500  # margem abaixo dos 10 mil oficiais

    def aguardar(self, textos):
        # Estimativa aproximada para português. O servidor valida o limite real.
        estimativa = sum(max(1, int(len(t) / 3.5) + 1) for t in textos)
        if estimativa > self.limite_tokens:
            raise ValueError(
                f"Uma requisição estimada em {estimativa} tokens excede o "
                f"limite seguro de {self.limite_tokens}. Reduza EMBEDDING_BATCH_SIZE."
            )
        while True:
            agora = time.monotonic()
            while self.chamadas and agora - self.chamadas[0][0] >= 65:
                self.chamadas.popleft()
            usados = sum(item[1] for item in self.chamadas)
            if len(self.chamadas) < 3 and usados + estimativa <= self.limite_tokens:
                self.chamadas.append((agora, estimativa))
                return
            espera = max(1.0, 65 - (agora - self.chamadas[0][0]))
            print(f"⏳ Limite gratuito Voyage: aguardando {espera:.0f}s...")
            time.sleep(espera)


# Grupos separados conforme painel da Voyage (embeddings e reranking).
# ATENÇÃO: o painel mostra dois grupos, mas não comprova independência
# das cotas. Respostas HTTP 429 continuam tratadas pelo retry abaixo.
LIMITADOR_EMBEDDINGS = VoyageFreeRateLimiter()
LIMITADOR_RERANK = VoyageFreeRateLimiter()


def requisicao_voyage(url, headers, payload, textos):
    """Retry apenas para falhas temporárias; erros de autenticação são fatais."""
    for tentativa in range(12):
        if url.rstrip("/").endswith("/embeddings"):
            limitador = LIMITADOR_EMBEDDINGS
        elif url.rstrip("/").endswith("/rerank"):
            limitador = LIMITADOR_RERANK
        else:
            raise ValueError(f"Endpoint Voyage não reconhecido: {url}")
        limitador.aguardar(textos)
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
        except (requests.Timeout, requests.ConnectionError) as exc:
            if tentativa == 11:
                raise
            espera = min(120, 10 * (tentativa + 1))
            print(f"⚠️ Falha temporária de rede: {exc}. Nova tentativa em {espera}s.")
            time.sleep(espera)
            continue
        if response.status_code in (429, 500, 502, 503, 504):
            if response.status_code == 429:
                # Exibe o motivo retornado pela Voyage para distinguir rate limit
                # temporário de uma eventual cota gratuita esgotada.
                detalhe = response.text[:500].replace("\n", " ")
                print(f"⚠️ Voyage HTTP 429: {detalhe}")
                # Não insistir por ~12 minutos no mesmo bloqueio.
                if tentativa >= 2:
                    response.raise_for_status()
            elif tentativa == 11:
                response.raise_for_status()
            retry_after = response.headers.get("Retry-After", "")
            try:
                espera = max(65.0, float(retry_after))
            except (ValueError, TypeError):
                espera = 65.0
            print(f"⚠️ Voyage HTTP {response.status_code}. Nova tentativa em {espera:.0f}s.")
            time.sleep(espera)
            continue
        if not response.ok:
            raise RuntimeError(f"Voyage HTTP {response.status_code}: {response.text[:1000]}")
        return response.json()
    raise RuntimeError("Voyage: esgotadas as tentativas de requisição.")


class HttpVoyageEmbeddings(Embeddings):
    def __init__(self, api_key, model_name=VOYAGE_EMBEDDING_MODEL):
        self.model_name = model_name
        self.url = "https://api.voyageai.com/v1/embeddings"
        self.headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    def _embed(self, texts, input_type):
        if not texts:
            return []
        embeddings = []
        # Agrupa chunks em lotes maiores, respeitando tanto a quantidade de
        # entradas quanto a estimativa conservadora de tokens por requisição.
        # Não altera o texto, a ordem dos vetores nem os parâmetros do modelo.
        inicio = 0
        while inicio < len(texts):
            fim = inicio
            tokens_estimados = 0
            while fim < len(texts) and fim - inicio < EMBEDDING_BATCH_SIZE:
                estimativa = max(1, int(len(texts[fim]) / 3.5) + 1)
                if fim > inicio and tokens_estimados + estimativa > EMBEDDING_MAX_TOKENS_ESTIMADOS:
                    break
                if estimativa > EMBEDDING_MAX_TOKENS_ESTIMADOS:
                    raise ValueError(
                        f"Entrada de embedding estimada em {estimativa} tokens; "
                        "excede o limite por lote configurado."
                    )
                tokens_estimados += estimativa
                fim += 1
            lote = texts[inicio:fim]
            payload = {"model": self.model_name, "input": lote, "input_type": input_type}
            dados = requisicao_voyage(self.url, self.headers, payload, lote)
            vetor_por_indice = sorted(dados["data"], key=lambda item: item["index"])
            if len(vetor_por_indice) != len(lote):
                raise RuntimeError("Voyage retornou quantidade inesperada de embeddings.")
            embeddings.extend(item["embedding"] for item in vetor_por_indice)
            inicio = fim
        return embeddings

    def embed_documents(self, texts):
        return self._embed(texts, "document")

    def embed_query(self, text):
        return self._embed([text], "query")[0]


class HttpVoyageRerank:
    def __init__(self, api_key, model_name=VOYAGE_RERANKER_MODEL):
        self.model_name = model_name
        self.url = "https://api.voyageai.com/v1/rerank"
        self.headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    def rerank(self, documents, query, top_n):
        if not documents:
            return [], []
        textos = [doc.page_content for doc in documents]
        payload = {"model": self.model_name, "query": query, "documents": textos,
                   "top_k": top_n, "return_documents": False}
        # No reranking, cada documento é avaliado em conjunto com a pergunta.
        dados = requisicao_voyage(self.url, self.headers, payload,
                                  [query + " " + texto for texto in textos])
        resultados = dados["data"]
        docs_ordenados = [documents[item["index"]] for item in resultados]
        scores = [float(item["relevance_score"]) for item in resultados]
        return docs_ordenados, scores


# ============================================================
# LEITURA DE MÚLTIPLOS PDFs E PRESERVAÇÃO DE METADADOS
# ============================================================

def carregar_pdfs(pasta_pdfs):
    if not pasta_pdfs.exists():
        raise FileNotFoundError(
            f"Pasta de PDFs não encontrada: {pasta_pdfs}\n"
            "Crie a pasta 'pdfs' ao lado deste script e coloque os PDFs nela."
        )

    arquivos_pdf = [pasta_pdfs / PDF_ATUAL] if PDF_ATUAL else sorted(pasta_pdfs.glob("*.pdf"))
    if not arquivos_pdf:
        raise FileNotFoundError(
            f"Nenhum PDF encontrado em {pasta_pdfs}. "
            "Coloque pelo menos um arquivo PDF nessa pasta."
        )

    documentos = []
    for caminho_pdf in arquivos_pdf:
        print(f"📄 Lendo: {caminho_pdf.name}")
        reader = PdfReader(str(caminho_pdf))

        for numero_pagina, pagina in enumerate(reader.pages, start=1):
            texto = pagina.extract_text() or ""
            texto = texto.strip()

            if texto:
                documentos.append(
                    Document(
                        page_content=texto,
                        metadata={
                            "source": caminho_pdf.name,
                            "page": numero_pagina,
                        },
                    )
                )

    if not documentos:
        raise ValueError(
            "Nenhum texto foi extraído dos PDFs. "
            "Eles podem ser digitalizações sem camada de texto; nesse caso, será necessário OCR."
        )

    print(
        f"✅ {len(arquivos_pdf)} PDF(s), "
        f"{len(documentos)} página(s) com texto extraído."
    )
    return documentos


def dividir_documentos(documentos, chunk_size, overlap):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", "; ", " ", ""],
        add_start_index=True,
    )

    chunks = splitter.split_documents(documentos)
    return [doc for doc in chunks if doc.page_content.strip()]


# ============================================================
# PERGUNTAS DE TESTE
# ============================================================

def carregar_perguntas(caminho_csv):
    if not caminho_csv.exists():
        exemplo = pd.DataFrame({
            "pergunta": [
                "Qual é o objetivo principal do documento?",
                "Quais são os conceitos ou etapas mais importantes?",
                "Quais limitações ou recomendações são apresentadas?",
            ],
            "documento_esperado": ["", "", ""],
            "paginas_relevantes": ["", "", ""],
        })
        exemplo.to_csv(caminho_csv, index=False, encoding="utf-8-sig")
        raise FileNotFoundError(
            f"Criei um modelo de perguntas em: {caminho_csv}\n"
            "Edite esse CSV com perguntas reais sobre seus PDFs e execute novamente."
        )

    df = pd.read_csv(caminho_csv).fillna("")
    if "pergunta" not in df.columns:
        raise ValueError(
            "O CSV de perguntas precisa ter uma coluna chamada 'pergunta'."
        )

    df["pergunta"] = df["pergunta"].astype(str).str.strip()
    df = df[df["pergunta"] != ""]

    if df.empty:
        raise ValueError("O arquivo de perguntas não contém perguntas válidas.")

    if "documento_esperado" not in df.columns:
        df["documento_esperado"] = ""

    if "paginas_relevantes" not in df.columns:
        df["paginas_relevantes"] = ""
    return df.to_dict(orient="records")



def interpretar_paginas(valor):
    """Aceita '2;5;7' (páginas numeradas a partir de 1)."""
    if pd.isna(valor) or not str(valor).strip():
        return set()
    try:
        paginas = {int(x.strip()) for x in str(valor).split(";") if x.strip()}
    except ValueError as e:
        raise ValueError(f"Páginas inválidas: {valor!r}. Use 2;5;7") from e
    if any(x < 1 for x in paginas):
        raise ValueError("As páginas devem começar em 1.")
    return paginas


def avaliar_paginas(docs, documento_esperado, paginas_relevantes):
    """Métricas de páginas relevantes com deduplicação de página.

    Precision@N: proporção dos chunks retornados cuja página é relevante.
    Recall@N: fração de páginas relevantes distintas encontradas.
    nDCG@N: ranking de chunks, com ganho apenas na primeira ocorrência
    de cada página relevante, evitando crédito repetido por sobreposição.
    """
    if not documento_esperado or not paginas_relevantes:
        return None
    esperado = Path(documento_esperado).name.casefold()
    vistos = set()
    relevantes_distintos = set()
    acertos_chunks = 0
    dcg = 0.0
    import math
    for pos, doc in enumerate(docs, start=1):
        fonte = Path(str(doc.metadata.get("source", ""))).name.casefold()
        pagina = int(doc.metadata.get("page", -1))
        chave = (fonte, pagina)
        relevante = fonte == esperado and pagina in paginas_relevantes
        acertos_chunks += int(relevante)
        if relevante:
            relevantes_distintos.add(pagina)
            if chave not in vistos:
                dcg += 1.0 / math.log2(pos + 1)
        vistos.add(chave)
    ideal = sum(1.0 / math.log2(i + 1) for i in range(1, min(len(docs), len(paginas_relevantes)) + 1))
    return {
        "precision": acertos_chunks / len(docs) if docs else 0.0,
        "recall": len(relevantes_distintos) / len(paginas_relevantes),
        "ndcg": dcg / ideal if ideal else 0.0,
    }


# ============================================================
# EXECUÇÃO DO BENCHMARK
# ============================================================

def executar_benchmark():
    api_key = os.getenv("VOYAGE_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Variável VOYAGE_API_KEY não encontrada. "
            "Verifique seu arquivo .env."
        )

    documentos = carregar_pdfs(PASTA_PDFS)
    perguntas = carregar_perguntas(ARQUIVO_PERGUNTAS)

    embeddings = HttpVoyageEmbeddings(api_key)
    reranker = HttpVoyageRerank(api_key)

    # Sem warm-up: a primeira indexação já valida a API, evitando uma chamada
    # cobrada e sujeita a rate limit em cada PDF.

    configuracoes = []
    for chunk_size, overlap_ratio, k, top_n in product(
        CHUNK_SIZES, OVERLAP_RATIOS, K_VALUES, TOP_N_VALUES
    ):
        overlap = int(chunk_size * overlap_ratio)
        if top_n < k:
            configuracoes.append((chunk_size, overlap, k, top_n))

    total = len(configuracoes)
    resultados = []

    # O CSV é escrito progressivamente para preservar resultados parciais.
    campos = [
        "Chunk Size (chars)",
        "Overlap (chars)",
        "Overlap (%)",
        "K Retriever",
        "Top N Reranker",
        "Quantidade de Chunks",
        "Tempo Indexação (s)",
        "Tempo Recuperação + Reranking Médio (s)",
        "Tempo Recuperação + Reranking P95 (s)",
        "Contexto Médio (chars)",
        "Contexto Médio (tokens estimados)",
        "Documentos Fonte Médios",
        "Score Reranker Médio",
        "Taxa Acerto Documento Esperado",
        "MRR Documento Esperado",
        "Quantidade de Perguntas Avaliadas",
        "Precision@N Páginas",
        "Recall@N Páginas",
        "nDCG@N Páginas",
        "Perguntas com Páginas Anotadas",
    ]

    campos_auditoria = ["Chunk Size (chars)", "Overlap (chars)", "K Retriever", "Top N Reranker", "Pergunta", "Posição", "Documento", "Página", "Score Reranker", "Texto Recuperado", "Relevância Humana (0-2)", "Observações"]
    campos_detalhes = [
        "Chunk Size (chars)", "Overlap (chars)", "K Retriever", "Top N Reranker",
        "Pergunta", "Documento Esperado", "Páginas Relevantes",
        "Fontes Recuperadas", "Páginas Recuperadas",
        "Precision@N Páginas", "Recall@N Páginas", "nDCG@N Páginas",
        "Latência (s)", "Chunks Recuperados JSON"
    ]
    # Recomeço seguro: somente configurações COMPLETAS são mantidas.
    # Linhas parciais de uma configuração interrompida são descartadas.
    def chave_config(linha):
        return (int(linha["Chunk Size (chars)"]), int(linha["Overlap (chars)"]),
                int(linha["K Retriever"]), int(linha["Top N Reranker"]))

    completos = set()
    if ARQUIVO_RESULTADOS.exists():
        anterior = pd.read_csv(ARQUIVO_RESULTADOS)
        if not anterior.empty:
            completos = {chave_config(linha) for linha in anterior.to_dict("records")}
            resultados.extend(anterior.to_dict("records"))
    for caminho in (ARQUIVO_DETALHES, ARQUIVO_AUDITORIA):
        if caminho.exists():
            antigo = pd.read_csv(caminho)
            if not antigo.empty:
                antigo = antigo[[chave_config(linha) in completos for linha in antigo.to_dict("records")]]
                antigo.to_csv(caminho, index=False, encoding="utf-8-sig")

    with open(ARQUIVO_RESULTADOS, "a", newline="", encoding="utf-8-sig") as arquivo_csv, \
         open(ARQUIVO_DETALHES, "a", newline="", encoding="utf-8-sig") as arquivo_detalhes, \
         open(ARQUIVO_AUDITORIA, "a", newline="", encoding="utf-8-sig") as arquivo_auditoria:
        writer = csv.DictWriter(arquivo_csv, fieldnames=campos)
        writer_detalhes = csv.DictWriter(arquivo_detalhes, fieldnames=campos_detalhes)
        writer_auditoria = csv.DictWriter(arquivo_auditoria, fieldnames=campos_auditoria)
        if ARQUIVO_AUDITORIA.stat().st_size == 0:
            writer_auditoria.writeheader()
        if ARQUIVO_DETALHES.stat().st_size == 0:
            writer_detalhes.writeheader()
        if ARQUIVO_RESULTADOS.stat().st_size == 0:
            writer.writeheader()

        for indice, (chunk_size, overlap, k, top_n) in enumerate(configuracoes, start=1):
            if (chunk_size, overlap, k, top_n) in completos:
                print(f"⏭️ [{indice}/{total}] configuração já concluída; ignorando.")
                continue
            persist_dir = None
            vectorstore = None

            print(
                f"\n[{indice}/{total}] chunk={chunk_size}, overlap={overlap}, "
                f"K={k}, TopN={top_n}"
            )

            try:
                chunks = dividir_documentos(documentos, chunk_size, overlap)
                if not chunks:
                    print("⚠️ Nenhum chunk gerado. Pulando configuração.")
                    continue

                inicio_indexacao = time.perf_counter()
                persist_dir = tempfile.mkdtemp(prefix="chroma_rag_benchmark_")

                collection_name = f"rag_{uuid.uuid4().hex[:12]}"
                vectorstore = Chroma.from_documents(
                    documents=chunks,
                    embedding=embeddings,
                    collection_name=collection_name,
                    persist_directory=persist_dir,
                )
                tempo_indexacao = time.perf_counter() - inicio_indexacao

                tempos = []
                tamanhos_contexto = []
                fontes_por_pergunta = []
                scores_reranker = []
                acertos_documento = []
                reciprocal_ranks = []
                metricas_paginas = []

                for item in perguntas:
                    pergunta = item["pergunta"]
                    documento_esperado = str(item.get("documento_esperado", "")).strip()
                    paginas_relevantes = interpretar_paginas(item.get("paginas_relevantes", ""))

                    inicio = time.perf_counter()
                    docs_brutos = vectorstore.similarity_search(
                        pergunta,
                        k=min(k, len(chunks)),
                    )
                    docs_reranqueados, scores = reranker.rerank(
                        docs_brutos,
                        pergunta,
                        min(top_n, len(docs_brutos)),
                    )
                    tempo_total = time.perf_counter() - inicio

                    contexto = "\n\n".join(
                        doc.page_content for doc in docs_reranqueados
                    )

                    tempos.append(tempo_total)
                    tamanhos_contexto.append(len(contexto))
                    fontes = {
                        doc.metadata.get("source", "desconhecido")
                        for doc in docs_reranqueados
                    }
                    fontes_por_pergunta.append(len(fontes))
                    scores_reranker.extend(scores)

                    avaliacao = avaliar_paginas(
                        docs_reranqueados, documento_esperado, paginas_relevantes
                    )
                    if avaliacao is not None:
                        metricas_paginas.append(avaliacao)
                    writer_detalhes.writerow({
                        "Chunk Size (chars)": chunk_size,
                        "Overlap (chars)": overlap,
                        "K Retriever": k,
                        "Top N Reranker": top_n,
                        "Pergunta": pergunta,
                        "Documento Esperado": documento_esperado,
                        "Páginas Relevantes": ";".join(map(str, sorted(paginas_relevantes))),
                        "Fontes Recuperadas": ";".join(str(d.metadata.get("source", "")) for d in docs_reranqueados),
                        "Páginas Recuperadas": ";".join(str(d.metadata.get("page", "")) for d in docs_reranqueados),
                        "Precision@N Páginas": avaliacao["precision"] if avaliacao else None,
                        "Recall@N Páginas": avaliacao["recall"] if avaliacao else None,
                        "nDCG@N Páginas": avaliacao["ndcg"] if avaliacao else None,
                        "Latência (s)": round(tempo_total, 4),
                        "Chunks Recuperados JSON": json.dumps([
                            {"posicao": i, "documento": str(d.metadata.get("source", "")),
                             "pagina": d.metadata.get("page"), "texto": d.page_content,
                             "score_reranker": float(scores[i-1]) if i-1 < len(scores) else None}
                            for i, d in enumerate(docs_reranqueados, 1)
                        ], ensure_ascii=False),
                    })
                    for pos, (doc, score) in enumerate(zip(docs_reranqueados, scores), start=1):
                        writer_auditoria.writerow({
                            "Chunk Size (chars)": chunk_size, "Overlap (chars)": overlap,
                            "K Retriever": k, "Top N Reranker": top_n,
                            "Pergunta": pergunta, "Posição": pos,
                            "Documento": doc.metadata.get("source", ""),
                            "Página": doc.metadata.get("page", ""),
                            "Score Reranker": round(float(score), 6),
                            "Texto Recuperado": doc.page_content,
                            "Relevância Humana (0-2)": "", "Observações": "",
                        })
                    arquivo_auditoria.flush()
                    arquivo_detalhes.flush()

                    # Avaliação opcional por documento esperado.
                    # Use o nome do PDF na coluna documento_esperado.
                    if documento_esperado:
                        nomes_recuperados = [
                            str(doc.metadata.get("source", "")).lower()
                            for doc in docs_reranqueados
                        ]
                        esperado = documento_esperado.lower()

                        posicoes = [
                            pos for pos, nome in enumerate(nomes_recuperados, start=1)
                            if esperado in nome
                        ]

                        acertos_documento.append(1.0 if posicoes else 0.0)
                        reciprocal_ranks.append(
                            1.0 / min(posicoes) if posicoes else 0.0
                        )

                # P95 calculado sem depender de bibliotecas estatísticas extras.
                tempo_p95 = float(pd.Series(tempos).quantile(0.95))

                resultado = {
                    "Chunk Size (chars)": chunk_size,
                    "Overlap (chars)": overlap,
                    "Overlap (%)": round(overlap / chunk_size, 2),
                    "K Retriever": k,
                    "Top N Reranker": top_n,
                    "Quantidade de Chunks": len(chunks),
                    "Tempo Indexação (s)": round(tempo_indexacao, 3),
                    "Tempo Recuperação + Reranking Médio (s)": round(mean(tempos), 3),
                    "Tempo Recuperação + Reranking P95 (s)": round(tempo_p95, 3),
                    "Contexto Médio (chars)": round(mean(tamanhos_contexto), 1),
                    # Estimativa grosseira; não equivale à contagem real de tokens.
                    "Contexto Médio (tokens estimados)": round(mean(tamanhos_contexto) / 4, 1),
                    "Documentos Fonte Médios": round(mean(fontes_por_pergunta), 2),
                    "Score Reranker Médio": (
                        round(mean(scores_reranker), 4) if scores_reranker else None
                    ),
                    "Taxa Acerto Documento Esperado": (
                        round(mean(acertos_documento), 4) if acertos_documento else None
                    ),
                    "MRR Documento Esperado": (
                        round(mean(reciprocal_ranks), 4) if reciprocal_ranks else None
                    ),
                    "Quantidade de Perguntas Avaliadas": len(perguntas),
                    "Precision@N Páginas": round(mean(x["precision"] for x in metricas_paginas), 4) if metricas_paginas else None,
                    "Recall@N Páginas": round(mean(x["recall"] for x in metricas_paginas), 4) if metricas_paginas else None,
                    "nDCG@N Páginas": round(mean(x["ndcg"] for x in metricas_paginas), 4) if metricas_paginas else None,
                    "Perguntas com Páginas Anotadas": len(metricas_paginas),
                }

                writer.writerow(resultado)
                arquivo_csv.flush()
                resultados.append(resultado)

                print(
                    f"✅ Indexação: {tempo_indexacao:.2f}s | "
                    f"Busca + rerank: {mean(tempos):.2f}s | "
                    f"Contexto: {mean(tamanhos_contexto):.0f} caracteres"
                )

            except Exception as erro:
                print(
                    f"❌ Falha nesta configuração "
                    f"(chunk={chunk_size}, overlap={overlap}, K={k}, TopN={top_n}): "
                    f"{erro}"
                )
                raise  # Falha interrompe; na próxima execução retoma configurações completas.

            finally:
                if vectorstore is not None:
                    del vectorstore
                if persist_dir:
                    shutil.rmtree(persist_dir, ignore_errors=True)

            time.sleep(PAUSA_ENTRE_CONFIGURACOES)

    if not resultados:
        raise RuntimeError(
            "Nenhuma configuração foi concluída. Confira os erros exibidos acima."
        )

    print(f"\n🏁 Benchmark concluído: {ARQUIVO_RESULTADOS}")
    print(f"Detalhes por pergunta: {ARQUIVO_DETALHES}")
    print(f"Auditoria de chunks: {ARQUIVO_AUDITORIA}")
    print(f"Configurações concluídas: {len(resultados)} de {total}")
    print(
        "\nATENÇÃO: score do reranker não é uma métrica de precisão calibrada. "
        "Para escolher a melhor configuração, use perguntas com documento esperado "
        "e, idealmente, relevância anotada por trecho."
    )


if __name__ == "__main__":
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(PASTA_PDFS.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"Nenhum PDF encontrado em {PASTA_PDFS}")

    # Validação antecipada: não iniciar chamadas à API com pares incompletos.
    for pdf in pdfs:
        perguntas_csv = PASTA_PERGUNTAS / f"perguntas_teste_{pdf.stem}.csv"
        if not perguntas_csv.is_file():
            raise FileNotFoundError(f"CSV correspondente não encontrado: {perguntas_csv}")
        perguntas_df = pd.read_csv(perguntas_csv).fillna("")
        if len(perguntas_df) != 15:
            raise ValueError(f"{perguntas_csv.name}: esperado exatamente 15 perguntas; recebido {len(perguntas_df)}.")
        if "documento_esperado" in perguntas_df.columns:
            nomes = {str(v).strip().casefold() for v in perguntas_df["documento_esperado"] if str(v).strip()}
            if nomes and nomes != {pdf.name.casefold()}:
                raise ValueError(
                    f"CSV {perguntas_csv.name}: documento_esperado={sorted(nomes)} "
                    f"não corresponde a {pdf.name}. Corrija o CSV antes de executar."
                )

    for indice, pdf in enumerate(pdfs, start=1):
        PDF_ATUAL = pdf.name
        ARQUIVO_PERGUNTAS = PASTA_PERGUNTAS / f"perguntas_teste_{pdf.stem}.csv"
        ARQUIVO_RESULTADOS = PASTA_RESULTADOS / f"benchmark_rag_multidocumentos_{pdf.stem}.csv"
        ARQUIVO_DETALHES = PASTA_RESULTADOS / f"benchmark_rag_detalhes_{pdf.stem}.csv"
        ARQUIVO_AUDITORIA = PASTA_RESULTADOS / f"auditoria_chunks_rag_{pdf.stem}.csv"

        print(f"\n{'=' * 60}\nPDF {indice}/{len(pdfs)}: {pdf.name}\n{'=' * 60}")
        executar_benchmark()

