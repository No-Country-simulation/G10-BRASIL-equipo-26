# Matriz de Decisões Técnicas e Status Real — MentorIA Tech

**Responsável:** Lídia Moura — Líder Técnica  
**Data da última atualização:** 19/11/2026  
**Objetivo:** Manter transparência absoluta entre o que já está implementado e validado no MVP, o que foi ajustado na otimização final e o que pertence ao roadmap Pós-MVP.

---

## 1. Quadro Geral de Status do Projeto

| Componente / Funcionalidade | Status Atual | Localização / Evidência no Repositório | Observação Técnica |
| :--- | :--- | :--- | :--- |
| **Identidade Nominal e Marca (`MentorIA Tech`)** | ✅ **IMPLEMENTADO E VALIDADO** | `README.md`, `assets/Logomarca_principal_1.webp`, `assets/mentoria-tech-logo-mascote-fundo-branco.jpg` | Aprovado em votação na reunião de 05/11/2026 (substituindo o codinome inicial *NovaMente*). |
| **Contratos de Dados Pydantic v2 (6 formatos)** | ✅ **IMPLEMENTADO E VALIDADO** | `rag/pipeline/schemas.py`, `docs/contrato-fastapi-frontend.md` | Valida `Tutorial`, `Flashcards`, `Quiz`, `TL;DR`, `Roteiro` e `Resumo` com `extra='forbid'` (contrato `v0.3`). |
| **Extrator Multi-Formato (`.pdf`, `.md`, `.txt`)** | ✅ **IMPLEMENTADO E VALIDADO** | `backend/app/ingestao.py` (PR #40) | Usa `pdfplumber` e extrai tabelas em Markdown, com validação de extensão e limite de `20 MiB`. |
| **Indexação Vetorial ChromaDB + Embeddings Gemini** | ✅ **IMPLEMENTADO E VALIDADO** | `rag/pipeline/rag_retrieval.py` | Usa `gemini-embedding-001` e `RecursiveCharacterTextSplitter` (2000/200), com timeout HTTP configurável (`GEMINI_TIMEOUT_MS`). |
| **Reranking Semântico e Avaliação de Documento** | ✅ **IMPLEMENTADO E VALIDADO** | `rag/pipeline/rag_retrieval.py`, `rag/pipeline/avaliacao_documento.py` | Top 5 de 10 candidatos com fallback vetorial e timeout HTTP padrão de `20s` (`20000 ms`). |
| **Orquestração LLM (`Groq -> Fallback Gemini`)** | ✅ **IMPLEMENTADO E VALIDADO** | `rag/pipeline/llm_pipeline.py` | Ordem padrão `LLM_PROVIDER_ORDER=groq,gemini` (`openai/gpt-oss-120b` primário + Gemini fallback com timeout `30s`), reduzindo Quiz de 5 questões para `13,7s`. |
| **Perfis Oficiais (`Iniciante`, `Jr/Pleno`, `Tech Lead`, `Gestor`)** | ✅ **IMPLEMENTADO E VALIDADO** | `rag/pipeline/schemas.py`, `app/config.py`, `tests/test_qa_pipeline.py` | Remoção do campo `nicho` e consolidação dos 4 perfis oficiais sem termos legados. |
| **Pool / Rotação de Múltiplas Chaves de API** | ✅ **IMPLEMENTADO E VALIDADO** | `services/oci_secrets.py`, `rag/pipeline/llm_pipeline.py` | Rotação automática entre múltiplas chaves (`GEMINI_API_KEYS`, `GROQ_API_KEYS`) para alta disponibilidade. |
| **Persistência Local SQLite + Pseudonimização LGPD** | ✅ **IMPLEMENTADO E VALIDADO** | `rag/database.py`, `rag/persistencia.py` | Tabelas `geracoes`, `respostas`, `eventos_estudo`, `avaliacoes_documento` e `telemetria_api` com hash SHA-256 (Zero PII). |
| **API FastAPI (`rag/main.py`) + Fluxo Quiz 3 Tentativas** | ✅ **IMPLEMENTADO E VALIDADO** | `rag/main.py` | Endpoints `/health`, `/geracoes`, `/quiz/rodadas`, `/quiz/respostas`, `/quiz/{id}/historico` sem vazamento de gabarito. |
| **Interface Web Streamlit Integrada à API + OCI** | ✅ **IMPLEMENTADO E VALIDADO** | `app/main.py`, `app/api_client.py`, `app/oci_bridge.py` | Publicada em [mentoria-tech.streamlit.app](https://mentoria-tech.streamlit.app/), com Tema Claro validado para o Demo Day. |
| **Persistência Ativa no OCI Object Storage (Always Free)** | ✅ **IMPLEMENTADO E VALIDADO** | `services/oci_storage.py`, `app/oci_bridge.py` | Bucket privado `mentoria-tech-artifacts` (`NoPublicAccess`) com upload real verificado e fallback local em `data/bi_exports/`. |
| **Exportação Analítica & Notebooks Data Science/BI** | ✅ **IMPLEMENTADO E VALIDADO** | `services/bi_exporter.py`, `data/bi_exports/`, `data_science/` | Exportação CSV sanitizada e notebooks de auditoria/validação (`relatorio_qa_bi_mentoria_tech.ipynb` e `validacao_pipeline_mentoria_tech.ipynb`). |
| **Benchmark RAG (200 experimentos)** | ✅ **IMPLEMENTADO E VALIDADO** | `rag/benchmark/` | 15 CSVs de auditoria + script + notebook de análise top 10. |
| **Suíte Automatizada de QA (`pytest`) & Relatórios** | ✅ **IMPLEMENTADO E VALIDADO** | `tests/`, `docs/relatorio-qa-evidencias.md` | `30` testes aprovados (`21/21` pipeline/API + `9/9` cliente HTTP) e relatórios trilíngues (PT-BR/ES/EN). |
| **Agentes Conversacionais (`agents/`)** | 🚀 **PÓS-MVP** | `agents/README.md` | Diretório reservado no roadmap para fluxos conversacionais multi-turno (LangGraph). |
| **OCI Vault & Autonomous Database** | 🚀 **PÓS-MVP** | `docs/integracao-oci.md`, `.env.example` | `USE_OCI_VAULT=false` no MVP pelo limite de 1 Vault por tenancy na camada Always Free. |
| **Dashboard Power BI Ativo, EN/ES na UI, Telegram, QR Code e OCR** | 🚀 **PÓS-MVP** | `docs/relatorio-qa-evidencias.md` | Não compõem o escopo de avaliação do MVP atual (hoje exporta CSVs para BI). |

---

## 2. Registro de Decisões de Arquitetura e Produto (ADR Resumido)

1. **ADR-01 — Processamento de Documento Único por Execução (Ata 26/10/2026):**
   * *Decisão:* O MVP processa um documento técnico por vez (`indice_documento`).
   * *Motivo:* Mitigar alucinações cruzadas entre documentos distintos e controlar o consumo de tokens na camada gratuita.
2. **ADR-02 — Escopo Estritamente Textual e em PT-BR no MVP (Atas 22/10 e 05/11/2026):**
   * *Decisão:* Focar 100% em entradas textuais (`.pdf`, `.md`, `.txt`) e saídas estruturadas em Português (PT-BR), com nicho 100% voltado à Educação em Tecnologia.
   * *Motivo:* Garantir excelência nos requisitos obrigatórios do edital dentro do prazo e das cotas gratuitas de LLM.
3. **ADR-03 — Escolha dos Parâmetros RAG via Benchmark (Ata 03/11/2026):**
   * *Decisão:* Adotar `CHUNK_SIZE=2000`, `CHUNK_OVERLAP=200`, `K_RETRIEVER=10` e `TOP_N_RERANKER=5`.
   * *Motivo:* Melhor equilíbrio entre métricas de recuperação (*Precision/Recall/NDCG*) e baixa latência nos 200 testes executados.
4. **ADR-04 — Orquestração Multi-Provedor `Groq -> Gemini` e Timeouts HTTP (Atualizado em 19/11/2026):**
   * *Decisão:* Priorizar Groq (`openai/gpt-oss-120b`) como provedor principal na etapa de geração (`LLM_PROVIDER_ORDER=groq,gemini`) mantendo Gemini como fallback automático (`30s`) e provedor de embeddings/avaliação/reranking (`20s` via `GEMINI_TIMEOUT_MS`).
   * *Motivo:* Auditoria da tabela `telemetria_api` comprovou que o Groq conclui gerações em ~`4,6s`–`5,7s`, enquanto chamadas Gemini sem timeout causavam travamentos acima de 60s; após o ajuste, o Quiz de 5 questões caiu de `60,4s`–`73s` para `13,7s`.
5. **ADR-05 — Privacidade por Padrão / LGPD (`rag/database.py`):**
   * *Decisão:* Não coletar nome, e-mail ou IP dos estudantes; utilizar hashes SHA-256 e UUIDs em todas as tabelas e object keys.
   * *Motivo:* Conformidade legal e segurança da informação desde o MVP.
6. **ADR-06 — Organização de Notebooks em `data_science/` e Dados em `data/bi_exports/` (19/11/2026):**
   * *Decisão:* Centralizar notebooks analíticos e de validação em `data_science/`, manter `data/bi_exports/` como saída ativa de exportação BI/fallback OCI e preservar `agents/` apenas como módulo documental Pós-MVP.
   * *Motivo:* Facilitar a manutenção contínua pelos analistas de Dados/BI sem misturar artefatos analíticos dentro do pacote de runtime `rag/`.
