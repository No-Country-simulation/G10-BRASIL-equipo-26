# Matriz de Decisões Técnicas e Status Real — MentorIA Tech

**Responsável:** Lídia Moura (Lidi) — Líder Técnica  
**Data da última atualização:** 09/11/2026  
**Objetivo:** Manter transparência absoluta entre o que já está implementado na `main`, o que está em revisão, o que é proposta arquitetural, o que está pendente para a reta final do MVP e o que foi classificado como Pós-MVP.

---

## 1. Quadro Geral de Status do Projeto

| Componente / Funcionalidade | Status Atual | Localização / Evidência no Repositório | Observação Técnica |
| :--- | :--- | :--- | :--- |
| **Identidade Nominal e Marca (`MentorIA Tech`)** | ✅ **IMPLEMENTADO** | `README.md`, `assets/Logomarca_principal_1.webp`, `assets/mentoria-tech-logo-mascote-fundo-branco.jpg` | Aprovado em votação na reunião de 05/11/2026 (substituindo o codinome inicial *NovaMente*). |
| **Contratos de Dados Pydantic v2 (6 formatos)** | ✅ **IMPLEMENTADO** | `rag/pipeline/schemas.py` | Valida `Tutorial`, `Flashcards`, `Quiz`, `TL;DR`, `Roteiro` e `Resumo` com `extra='forbid'`. |
| **Indexação Vetorial ChromaDB + Embeddings Gemini** | ✅ **IMPLEMENTADO** | `rag/pipeline/rag_retrieval.py` | Usa `gemini-embedding-001` e `RecursiveCharacterTextSplitter` (2000/200). |
| **Reranking Semântico com Fallback Vetorial** | ✅ **IMPLEMENTADO** | `rag/pipeline/rag_retrieval.py` | Usa `gemini-2.5-flash` para selecionar Top 5 de 10 candidatos. |
| **Orquestração LLM (Gemini -> Fallback Groq)** | ✅ **IMPLEMENTADO** | `rag/pipeline/llm_pipeline.py` | Valida JSON e referências de `chunk_ids`/páginas antes de aceitar a resposta. |
| **Persistência Local SQLite + Pseudonimização LGPD** | ✅ **IMPLEMENTADO** | `rag/database.py`, `rag/persistencia.py` | Tabelas `geracoes`, `respostas` e `eventos_estudo` com hash SHA-256 e exportação CSV. |
| **Benchmark RAG (200 experimentos)** | ✅ **IMPLEMENTADO** | `rag/benchmark/` | 15 CSVs de auditoria + script + notebook de análise top 10. |
| **Interface Web Streamlit (4 Telas UX/UI)** | ✅ **IMPLEMENTADO (Mock)** | `app/main.py` | Visual completo conforme Brandbook, operando atualmente sobre função mockada local. |
| **Extrator Definitivo Multi-Formato (`.pdf`, `.md`, `.txt`)** | 🔄 **EM REVISÃO** | **PR #40** (`feature/extrator-fase2` -> `rag/ingestao.py`) | Usa `pdfplumber` e extrai tabelas em Markdown. Requer remoção de código duplicado (linhas 106–204) e inclusão de `pdfplumber` no `requirements.txt`. |
| **Ajuste de Perfis (`Tech Lead` e `Executivo`) e Mensagens UX** | 🔄 **EM REVISÃO** | Solicitado pela frente de RAG (Rodrigo Silva / Lídia Moura) | Atualização de `Arquiteto` -> `Tech Lead` e `Gestor` -> `Executivo` + aviso amigável quando o documento não tiver escopo executivo ou camada de texto. |
| **Pool / Rotação de Múltiplas Chaves de API** | 🔄 **EM REVISÃO** | `rag/pipeline/llm_pipeline.py` | Permite cadastrar múltiplas chaves da equipe (`GEMINI_API_KEYS`, `GROQ_API_KEYS`) para evitar bloqueio por cota gratuita no Demo Day. |
| **Governança OCI (Grupos, Policies, Vault, Buckets)** | 📝 **PROPOSTA** | `docs/integracao-oci.md`, `docs/oci-tutorial.md` | Planejamento completo e seguro pronto para execução controlada no compartimento `mentoria-tech`. |
| **Integração com OCI Autonomous Database** | 📝 **PROPOSTA** | `docs/integracao-oci.md` | Modelagem de 6 entidades relacionais pronta; aguarda validação final do schema de feedback. |
| **Conexão Frontend (`app/main.py`) ↔ Backend (`rag/`)** | ⏳ **PENDENTE** | Frente conduzida pelos desenvolvedores de integração | Conectar o botão "Gerar conteúdo educacional" do Streamlit ao pipeline real em `rag/pipeline/`. |
| **Persistência Ativa no OCI Object Storage** | ⏳ **PENDENTE** | Requisito obrigatório do edital NoCountry | Conectar o upload real do documento e do JSON validado para os buckets privados da camada Always Free. |
| **Dashboard no Power BI** | 🚀 **PÓS-MVP** | Apenas modelo de dados e exportação CSV no MVP | A conexão ativa do Power BI ficará para a etapa pós-entrega do MVP. |
| **Idiomas Espanhol e Inglês** | 🚀 **PÓS-MVP** | MVP 100% em **PT-BR** | Idioma obrigatório do MVP é Português (PT-BR). |
| **Bot no Telegram, QR Code, Chat Livre e OCR** | 🚀 **PÓS-MVP** | Registrados como evolução futura | Não compõem o escopo de avaliação do MVP atual. |

---

## 2. Registro de Decisões de Arquitetura e Produto (ADR Resumido)

1. **ADR-01 — Processamento de Documento Único por Execução (Ata 26/10/2026):**
   * *Decisão:* O MVP processa um documento técnico por vez (` indice_documento`).
   * *Motivo:* Mitigar alucinações cruzadas entre documentos distintos e controlar o consumo de tokens na camada gratuita.
2. **ADR-02 — Escopo Estritamente Textual e em PT-BR no MVP (Atas 22/10 e 05/11/2026):**
   * *Decisão:* Focar 100% em entradas textuais (`.pdf`, `.md`, `.txt`) e saídas estruturadas em Português (PT-BR).
   * *Motivo:* Garantir excelência nos requisitos obrigatórios do edital dentro do prazo e das cotas gratuitas de LLM.
3. **ADR-03 — Escolha dos Parâmetros RAG via Benchmark (Ata 03/11/2026):**
   * *Decisão:* Adotar `CHUNK_SIZE=2000`, `CHUNK_OVERLAP=200`, `K_RETRIEVER=10` e `TOP_N_RERANKER=5`.
   * *Motivo:* Melhor equilíbrio entre métricas de recuperação (*Precision/Recall/NDCG*) e baixa latência nos 200 testes executados.
4. **ADR-04 — Contingência Multi-Provedor Gemini + Groq (Ata 03/11 e 05/11/2026):**
   * *Decisão:* Utilizar Google Gemini como provedor principal e Groq (`openai/gpt-oss-120b`) como fallback automático.
   * *Motivo:* Proteger a demonstração ao vivo contra erros `429 RESOURCE_EXHAUSTED` ou indisponibilidades momentâneas.
5. **ADR-05 — Privacidade por Padrão / LGPD (`rag/database.py`):**
   * *Decisão:* Não coletar nome, e-mail ou IP dos estudantes; utilizar hashes SHA-256 e UUIDs em todas as tabelas e object keys.
   * *Motivo:* Conformidade legal e segurança da informação desde o MVP.
