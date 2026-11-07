"""Configuração A selecionada no benchmark (proxy Voyage), agora com Gemini.

O desempenho de recuperação com Gemini ainda deve ser validado.
"""
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200
K_RETRIEVER = 10
TOP_N_RERANKER = 5
EMBEDDING_MODEL = 'gemini-embedding-001'
RERANKER_MODEL = 'gemini-2.5-flash'
