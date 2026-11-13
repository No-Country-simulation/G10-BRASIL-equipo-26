# Definição de Métricas, KPIs e Modelo Analítico — MentorIA Tech

**Responsável:** Lídia Moura (Lidi) — Líder Técnica (com contribuições de Rodrigo Silva, Vagner Marques e Equipe de Dados/BI)  
**Data da última atualização:** 09/11/2026  
**Status:** `IMPLEMENTADO NO PIPELINE / SQLITE` (Conexão ativa com Power BI classificada como `PÓS-MVP`)

---

## 1. Visão Geral do Sistema de Métricas

O **MentorIA Tech** foi desenhado para não ser uma "caixa-preta". Cada execução do pipeline coleta indicadores objetivos divididos em **3 dimensões**:
1. **KPIs de Qualidade de Recuperação (RAG Benchmark):** validam se os trechos certos do documento estão sendo entregues à LLM.
2. **KPIs Operacionais e de Confiabilidade do Pipeline (Runtime):** monitoram latência por etapa, conformidade estrutural JSON/Pydantic, ancoragem de citações e acionamento de fallback.
3. **KPIs Pedagógicos e de Produto (Interação e Feedback):** medem desempenho do estudante nos Quizzes, tempo de resposta e utilidade percebida do material gerado.

---

## 2. KPIs de Qualidade RAG (Benchmark Experimental — 200 Combinações)

Executado sobre **5 documentos técnicos** (`Machine_Learning.pdf`, `Deep_learning.pdf`, `LLM.pdf`, `redes_neurais.pdf`, `vcn-deployment-guide.pdf`), totalizando **82 páginas**, **75 perguntas de teste** e **40 configurações por documento** (`rag/benchmark/`):

| Métrica | O que mede | Papel na Decisão Arquitetural |
| :--- | :--- | :--- |
| **Precision@K** | Proporção dos trechos recuperados que contêm as páginas de referência corretas. | Evita poluir o prompt da LLM com páginas irrelevantes (reduz custo de tokens e distração). |
| **Recall@K** | Proporção das páginas de referência esperadas que foram efetivamente recuperadas nos Top-K chunks. | Garante que nenhuma informação essencial do documento fique de fora da resposta. |
| **Hit Rate** | Percentual de consultas em que pelo menos 1 trecho relevante foi recuperado no Top-N final. | Mede a confiabilidade mínima da busca semântica. |
| **MRR (Mean Reciprocal Rank)** | Avalia quão próximo do topo (1ª posição) aparece o primeiro trecho relevante. | Valida a eficácia do Reranker em priorizar a melhor evidência logo no início do contexto. |
| **NDCG (Normalized Discounted Cumulative Gain)** | Qualidade da ordenação completa dos trechos após o reranking. | Critério de desempate para escolher `CHUNK_SIZE=2000`, `OVERLAP=200`, `K=10` e `TOP_N=5`. |

---

## 3. KPIs de Execução do Pipeline e Validação (Runtime)

Registrados a cada geração pelo pipeline (`rag/pipeline/llm_pipeline.py`, `rag/database.py` e notebook de validação):

| Campo / Indicador | Tipo / Unidade | Descrição e Meta no MVP |
| :--- | :--- | :--- |
| `modelo_llm` / `provedor` | Texto (`chamar_gemini` / `chamar_groq`) | Identifica se a geração foi atendida pelo provedor primário ou pelo fallback. |
| `versao_prompt` | Texto (`rag-llm-v1`) | Rastreabilidade de qual versão de engenharia de prompt gerou o pacote. |
| `perfil` / `formato` / `idioma` | Categorias (`PT-BR`) | Dimensões de corte para análise de uso por persona e tipo de material. |
| `tempo_extracao_ms` | Milissegundos (`ms`) | Tempo gasto na leitura e limpeza do arquivo (`.pdf`, `.md`, `.txt`). |
| `tempo_recuperacao_ms` | Milissegundos (`ms`) | Tempo de chunking + embeddings + busca ChromaDB + reranking. |
| `duracao_geracao_ms` | Milissegundos (`ms`) | Latência de inferência da LLM + validação Pydantic (registrado na tabela `geracoes`). |
| `tempo_total_ms` | Milissegundos (`ms`) | Tempo ponta a ponta (Meta do MVP: `< 60.000 ms` por formato). |
| `quantidade_chunks` | Inteiro | Total de blocos indexados do documento de origem. |
| `json_valido` | Booleano (`1` / `0`) | Meta: **100%** dos pacotes persistidos devem passar por `PacoteFinal.model_validate()`. |
| `referencias_encontradas` | Booleano / Contagem | Verifica se todos os `chunk_ids` e páginas citadas pertencem ao `ContextoRAG`. |
| `erros_anteriores` | Lista / Texto | Registra se houve erro `429` ou `503` antes do fallback assumir a requisição. |

---

## 4. KPIs Pedagógicos e de Produto (`rag/database.py`)

Implementados nas tabelas `geracoes`, `respostas` e `eventos_estudo` (e expandidos com `feedbacks`):

1. **Taxa de Acerto em Quizzes (`taxa_acerto_pct`):** `ROUND(AVG(acertou) * 100, 2)` agrupado por `assunto`, `subassunto`, `dificuldade` e `tentativa_numero` (1ª, 2ª ou 3ª tentativa).
2. **Tempo Médio de Resposta (`tempo_medio_resposta_segundos`):** permite identificar questões ou tópicos onde o estudante apresenta maior dúvida.
3. **Índice de Satisfação / Utilidade (`feedback`):** avaliação da geração pelo usuário vinculada ao `geracao_id` e `sessao_id` (nota de 1 a 5 e indicador booleano de utilidade pedagógica).

---

## 5. Modelo de Dados Preparado para Power BI (Pós-MVP)

> **Diretriz de Escopo:** A construção do dashboard ativo no Power BI é uma entrega **PÓS-MVP**. No MVP atual, deixamos o **Modelo Estrela (Star Schema)** e a **exportação CSV (`database.export_csv`)** 100% prontos e padronizados.

### 5.1.Tabelas Exportáveis (`rag/database.py` -> CSV / OCI Object Storage)
* **Fato Gerações (`geracoes.csv`):**
  ```csv
  geracao_id,data_hora,usuario_id,sessao_id,documento_id,perfil,formato,nicho,nivel,quantidade_itens,tempo_estimado_estudo_minutos,ancoragem_fonte_score,modelo_llm,duracao_geracao_ms
  ```
* **Fato Respostas Quiz (`respostas.csv`):**
  ```csv
  resposta_id,data_hora,geracao_id,usuario_id,sessao_id,questao_indice,questao_id,assunto,subassunto,dificuldade,alternativa_escolhida,acertou,tempo_resposta_segundos,tentativa_numero,rodada_id,assunto_id,questao_referencia_id
  ```
* **Fato Eventos de Estudo (`eventos_estudo.csv`):**
  ```csv
  evento_id,data_hora,geracao_id,usuario_id,sessao_id,tipo_evento,item_indice
  ```
* **Fato Feedback do Usuário (`feedbacks.csv` — em integração):**
  ```csv
  feedback_id,data_hora,geracao_id,usuario_id,sessao_id,avaliacao_nota,util,comentario
  ```
* **Resumo Consolidado STAR (`star_metrics.csv` — padrão `hub-os-guIA`):**
  ```csv
  project_id,date,metric,before,after,unit,source,validation_method,validated_by,status,public_approved,notes
  ```
