# Plano de QA, Testes Automatizados e Validação pelo Método STAR — MentorIA Tech

**Responsável:** Lídia Moura (Lidi) — Líder Técnica (com contribuições de Rodrigo Silva, Lysara Pinheiro, Andrea Gonzalez e Vinicius Ferreira)  
**Data da última atualização:** 09/11/2026  
**Status:** Plano de Qualidade Oficial do MVP (Fases 6 e 8)

---

## 1. Estratégia de Garantia de Qualidade (QA)

A estratégia de QA do **MentorIA Tech** combina três camadas complementares:
1. **Validação Contínua por Contrato (Runtime QA):** O próprio pipeline recusa qualquer saída da LLM que viole os schemas Pydantic v2 (`extra='forbid'`) ou que invente `chunk_ids`/páginas fora dos trechos recuperados.
2. **Suíte de Testes Automatizados Reprodutíveis (`pytest` — 16 Cenários Obrigatórios):** Valida entradas válidas/inválidas, falhas de extração, ausência de contexto, validação de JSON, failover entre provedores, persistência SQLite e varredura de segurança contra vazamento de segredos.
3. **Documentação de Evidências pelo Método STAR:** Registro estruturado (*Situation, Task, Action, Result*) dos cenários de teste executados sobre documentos reais.

---

## 2. Matriz dos 16 Cenários Obrigatórios de Teste Automatizado (Fase 6)

| # | Cenário de Teste | Componente Alvo | Comportamento Esperado (Critério de Aceite) |
| :--- | :--- | :--- | :--- |
| **01** | **PDF válido** | Extração (`extrair_pdf` / `processar_documento`) | Retorna `DocumentoExtraido` válido com `tipo_arquivo='pdf'` e lista de `PaginaExtraida` >= 1. |
| **02** | **Markdown (`.md`) válido** | Extração multi-formato (`ingestao.py`) | Extrai texto limpo, normaliza quebras de linha e retorna `DocumentoExtraido` com `tipo_arquivo='md'`. |
| **03** | **TXT (`.txt`) válido** | Extração multi-formato (`ingestao.py`) | Lê UTF-8/UTF-8-SIG, remove espaços excedentes e retorna `DocumentoExtraido` com `tipo_arquivo='txt'`. |
| **04** | **Arquivo vazio** | Extração / Validação de entrada | Levanta exceção clara (`ValueError` / `RuntimeError`) informando ausência de conteúdo textual válido. |
| **05** | **Extensão inválida (ex.: `.exe`, `.docx`, `.png`)** | Validação de arquivo / Schema `DocumentoEntrada` | Rejeita imediatamente antes do processamento com mensagem explícita de formato não suportado. |
| **06** | **Documento sem texto (ex.: PDF escaneado em branco)** | Extração de PDF / Indexação RAG | Bloqueia o envio para o ChromaDB e informa que o documento não contém camada de texto extraível. |
| **07** | **Falha de extração (arquivo inexistente ou corrompido)** | Extração | Levanta `FileNotFoundError` ou erro controlado de leitura sem expor caminhos sensíveis do servidor. |
| **08** | **Recuperação sem contexto / contexto insuficiente** | `_contexto_texto` e `_validar_conteudo` (`llm_pipeline.py`) | Quando a LLM retorna `{"erro": "contexto_insuficiente"}` ou o limite é zero, levanta `FalhaGeracao` amigável. |
| **09** | **JSON inválido retornado pela LLM** | `_validar_conteudo` (`llm_pipeline.py`) | Captura `JSONDecodeError` e converte em `FalhaGeracao("A LLM não retornou JSON válido")`, acionando fallback se disponível. |
| **10** | **Validação Pydantic e integridade de referências** | `schemas.py` e `_validar_conteudo` | Rejeita alternativas duplicadas no Quiz, formatos trocados, `chunk_ids` inexistentes ou páginas fora do chunk citado. |
| **11** | **Falha de todos os provedores LLM** | `gerar_de_contexto` (`llm_pipeline.py`) | Quando Gemini e Groq falham, levanta `FalhaGeracao` consolidando os erros truncados sem vazar chaves ou prompts. |
| **12** | **Fallback automático (Gemini falha -> Groq assume)** | `gerar_de_contexto` (`llm_pipeline.py`) | Simula falha no provedor primário e comprova geração bem-sucedida pelo provedor secundário, preenchendo `erros_anteriores`. |
| **13** | **Registro de geração no banco SQLite** | `database.save_geracao` / `persistencia.registrar_geracao` | Persiste `PacoteFinal` na tabela `geracoes` e recupera exatamente o mesmo JSON via `get_pacote_json(geracao_id)`. |
| **14** | **Registro de feedback e respostas de Quiz** | `database.save_resposta` / `save_feedback` | Registra tentativa de resposta (bloqueando após acerto ou 3ª tentativa) e persiste avaliação de feedback da sessão. |
| **15** | **Persistência de eventos de estudo e exportação CSV** | `database.save_event` / `database.export_csv` | Insere eventos na tabela `eventos_estudo` e exporta CSV válido contendo os cabeçalhos esperados. |
| **16** | **Ausência de segredos no código e nos arquivos rastreados** | Auditoria estática de segurança (Repo Scan) | Verifica que nenhum arquivo versionado contém chaves reais (`AIza...`, `gsk_...`, `sk-...`), `.env` real ou bancos `.db`. |

---

## 3. Validação pelo Método STAR (Fase 8)

### STAR 01 — Validação Integrada dos 6 Formatos Pedagógicos com Fallback Resiliente
* **Situation (Situação):**
  * Era necessário comprovar que o pipeline real do **MentorIA Tech** (`rag/pipeline/`) conseguia ingerir um documento técnico real em português (`rag/Machine_Learning.pdf`, 16 páginas), indexá-lo vetorialmente e gerar os 6 formatos pedagógicos exigidos sem interromper a execução mesmo sob limites de taxa (*Rate Limit* `429`) da camada gratuita da API principal.
* **Task (Tarefa):**
  * Extrair as 16 páginas do PDF, indexar os chunks no `ChromaDB`, recuperar e reclassificar os trechos mais relevantes para cada formato e gerar `Tutorial`, `Flashcards`, `Quiz`, `TL;DR`, `Roteiro` e `Resumo` em **PT-BR** para o perfil `Iniciante`, validando 100% das saídas com Pydantic v2 e persistindo os registros no SQLite.
* **Action (Ação):**
  * Executado o script integrado `rag/teste_integracao.py` configurado com `CHUNK_SIZE=2000`, `CHUNK_OVERLAP=200`, `K_RETRIEVER=10`, `TOP_N_RERANKER=5`, embeddings `gemini-embedding-001`, reranker `gemini-2.5-flash`, prompt `rag-llm-v1`, provedor primário Google Gemini e fallback automático Groq (`openai/gpt-oss-120b`).
* **Result (Resultado):**
  * **Páginas extraídas / com texto:** `16 / 16` páginas (100% de aproveitamento textual).
  * **Chunks indexados:** `16` chunks reutilizados em memória para todas as 6 consultas.
  * **Taxa de sucesso na geração:** `6 / 6` formatos gerados e validados (100%).
  * **Atuação do Fallback:** `2` formatos gerados diretamente pelo Gemini (`Tutorial`, `Quiz`) e `4` formatos assumidos automaticamente pelo fallback Groq (`Flashcards`, `TL;DR`, `Roteiro`, `Resumo`) sem queda da aplicação.
  * **Validade do JSON e Referências:** `100%` dos pacotes aprovados por `PacoteFinal.model_validate()`, com todas as páginas e `chunk_ids` verificados contra os trechos recuperados (evidências salvas em `rag/visualizar_resultados_teste.ipynb`).
  * **Conclusão:** Pipeline validado ponta a ponta com resiliência comprovada contra falhas de cota de API.

---

### STAR 02 — Benchmark Experimental de Otimização de Hiperparâmetros RAG
* **Situation (Situação):**
  * Escolher arbitrariamente o tamanho de chunk e a quantidade de trechos recuperados em sistemas RAG pode causar perda de contexto técnico ou excesso de ruído e latência na geração educacional.
* **Task (Tarefa):**
  * Encontrar experimentalmente a configuração de melhor equilíbrio entre qualidade de recuperação (*Precision*, *Recall*, *NDCG*, *MRR*, *Hit Rate*) e tempo de resposta sobre múltiplos documentos técnicos de TI e IA.
* **Action (Ação):**
  * Executado o estudo experimental (`rag/benchmark/`) sobre **5 documentos técnicos** (`Machine_Learning.pdf`, `Deep_learning.pdf`, `LLM.pdf`, `redes_neurais.pdf`, `vcn-deployment-guide.pdf` — 82 páginas totais e 75 perguntas de referência), avaliando **40 configurações por documento** (`chunk_size` em 500, 1000, 1500, 2000; `overlap` em 10% e 20%; `K` em 5, 10, 15; `Top N` em 3 e 5), totalizando **200 execuções auditadas em CSV**.
* **Result (Resultado):**
  * Selecionada a **Configuração A (`CHUNK_SIZE=2000`, `CHUNK_OVERLAP=200`, `K=10`, `TOP_N=5`)**, que apresentou excelente cobertura semântica com tempo de recuperação significativamente menor do que configurações de chunks muito fragmentados.
  * Todos os 15 arquivos CSV de auditoria e o notebook `analisar_benchmark_top10_5_pdfs.ipynb` foram versionados em `rag/benchmark/` para total reprodutibilidade científica.

---

### STAR 03 — Adaptação Multi-Perfil (Iniciante vs. Desenvolvedor vs. Liderança)
* **Situation (Situação):**
  * O requisito central do Hackathon ONE G10 exige demonstrar como um mesmo documento técnico é adaptado para pelo menos 3 cenários/perfis distintos mantendo fidelidade à fonte.
* **Task (Tarefa):**
  * Validar a geração parametrizada combinando: (1) `Iniciante + Flashcards + PT-BR`, (2) `Jr/Pleno (Desenvolvedor) + Tutorial + PT-BR`, e (3) `Arquiteto/Gestor (Liderança) + Resumo/TL;DR ou Quiz + PT-BR`.
* **Action (Ação):**
  * Parametrização de `PedidoGeracao` injetando perfil, formato, nicho e nível no prompt estruturado `rag-llm-v1` com validação de saída específica por discriminador Pydantic (`Flashcards`, `Tutorial`, `ResumoTLDR`/`Quiz`).
* **Result (Resultado):**
  * Geração de pacotes distintos em estrutura, profundidade e foco pedagógico a partir da mesma base indexada, preservando em todos os casos a rastreabilidade de `chunk_ids` e páginas e registrando telemetria em SQLite.
