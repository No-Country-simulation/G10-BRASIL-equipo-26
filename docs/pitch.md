# Pitch & AI Canvas — MentorIA Tech (Equipe 26 | Hackathon ONE G10)

**Responsável:** Lídia Moura (Lidi) — Líder Técnica (com revisão da Equipe 26)  
**Data da última atualização:** 09/11/2026  
**Status:** Documentação de Produto e Estratégia do MVP (Alinhada às Atas de 19/10 a 05/11/2026)

---

## 1. Pitch Statement Oficial

> **O MentorIA Tech transforma documentações técnicas densas em materiais de estudo personalizados (Flashcards, Quizzes, Tutoriais, Roteiros e Resumos Executivos) para diferentes perfis de tecnologia em minutos, utilizando RAG e IA Generativa com validação rigorosa de fontes para garantir fidelidade técnica sem alucinações.**

---

## 2. Estrutura Executiva do Pitch (7 Pilares)

### 2.1. O que fazemos
Desenvolvemos uma plataforma inteligente de adaptação e geração de conteúdo educacional técnico que recebe um documento técnico real (`.pdf`, `.md` ou `.txt`) e gera pacotes de aprendizagem estruturados em JSON e visualizáveis em interface amigável, adaptando o vocabulário, os exemplos e a profundidade ao perfil exato de quem vai estudar.

### 2.2. Para quem (Público Prioritário)
* **Público Primário (Foco da Banca e Validação):** Estudantes de tecnologia e profissionais em transição de carreira que enfrentam barreiras ao estudar manuais oficiais densos (como documentações de nuvem OCI, redes VCN, engenharia de dados e Machine Learning).
* **Público Secundário:**
  * **Desenvolvedores Júnior / Pleno:** precisam de tutoriais práticos passo a passo ancorados na documentação oficial.
  * **Tech Leads / Arquitetos:** precisam avaliar trade-offs arquiteturais, segurança e limites técnicos rapidamente.
  * **Perfis Executivos / Gestores e EdTechs:** precisam transformar manuais técnicos em sínteses executivas (`TL;DR`) ou materiais de capacitação corporativa em escala.

### 2.3. Qual problema resolvemos
1. **Inacessibilidade cognitiva:** Documentações técnicas são escritas como referência de engenharia, não como material pedagógico. Um mesmo documento precisa ser explicado de forma completamente diferente para um iniciante e para um arquiteto.
2. **Gargalo de tempo e custo:** Designers instrucionais e líderes técnicos levam dias ou semanas para transformar manuais em trilhas, quizzes e flashcards atualizados.
3. **Risco de alucinação em IAs genéricas:** Pedir resumos em chats comuns de IA frequentemente introduz conceitos inventados ou desatualizados, sem indicar em qual página da documentação original a informação está.

### 2.4. Como resolvemos
Combinamos um pipeline enxuto e auditável em 8 etapas:
1. **Ingestão e Limpeza:** Leitura de documentos técnicos e estruturação por página (`DocumentoExtraido`).
2. **Segmentação Inteligente (Chunking):** Divisão em blocos de `2.000` caracteres com `200` de sobreposição (parâmetros definidos após benchmark experimental com 200 combinações).
3. **Indexação Vetorial:** Geração de embeddings (`gemini-embedding-001`) e armazenamento em `ChromaDB`.
4. **Recuperação + Reranking Semântico:** Busca dos `10` candidatos mais próximos e reclassificação dos `5` melhores trechos com `gemini-2.5-flash`.
5. **Orquestração Multi-Provedor com Fallback:** Geração parametrizada por `Perfil`, `Formato`, `Nicho` e `Nível` via Google Gemini (provedor principal) com contingência automática para Groq (`openai/gpt-oss-120b`).
6. **Validação Determinística (Pydantic v2 + Grounding Estrutural):** O sistema rejeita qualquer saída cujo JSON viole o schema ou que cite `chunk_ids`/páginas inexistentes nos trechos recuperados.
7. **Persistência e Telemetria Anonimizada:** Registro local em SQLite (`geracoes`, `respostas` de quiz e `eventos_estudo`) com hashes SHA-256 (sem coleta de PII) e integração planejada com **OCI Object Storage Always Free** e **Autonomous Database**.

### 2.5. Benefício Mensurável
* **Redução drástica no tempo de preparação:** Transforma a criação de 6 formatos pedagógicos (de semanas de trabalho manual) em **menos de 60 segundos de execução automatizada**.
* **Confiabilidade e Rastreabilidade:** 100% dos itens gerados carregam a referência explícita de página e `chunk_id` do documento de origem.

### 2.6. Diferencial Competitivo
1. **Adaptação Multi-Dimensional Real:** Não faz apenas um resumo genérico; cruza **Perfil** (`Iniciante`, `Jr/Pleno`, `Tech Lead/Arquiteto`, `Executivo/Gestor`) × **Formato** (`Tutorial`, `Flashcards`, `Quiz`, `TL;DR`, `Roteiro`, `Resumo`) × **Nicho** (`Geral`, `Fintech`, `Saúde`, `E-commerce`).
2. **Engenharia Baseada em Evidências (Benchmark RAG):** Os hiperparâmetros de recuperação não foram escolhidos por intuição, mas selecionados a partir de uma bateria de 200 experimentos auditáveis em 5 documentos técnicos.
3. **Resiliência e Governança by Design:** Arquitetura com fallback entre provedores de LLM, validação Pydantic v2 estrita (`extra='forbid'`) e privacidade nativa (LGPD).

### 2.7. Limite do MVP (Foco e Realismo)
* **O que FAZ parte do MVP:** Processamento de **1 documento por execução**, entradas textuais (`.pdf` com camada de texto, `.md`, `.txt`), idioma **PT-BR**, 4 perfis, 6 formatos estruturados em JSON, interface web Streamlit, persistência local SQLite e armazenamento de objetos no **OCI Object Storage (Always Free)**.
* **O que NÃO faz parte do MVP (Pós-MVP):** OCR para PDFs escaneados como imagem, múltiplos documentos simultâneos na mesma consulta, chat conversacional aberto, bot no Telegram, geração de QR Code, tradução automática para Espanhol/Inglês e conexão ativa em tempo real com Power BI.

---

## 3. AI Canvas — MentorIA Tech (Referência Metodológica `hub-os-guIA`)

Estrutura consolidada seguindo o framework de diagnóstico estratégico (*Jobs-to-be-Done + AI Canvas + Governança LGPD/STAR*), separando claramente fatos implementados de hipóteses em validação:

| Bloco do AI Canvas | Definição Estratégica no Projeto MentorIA Tech | Status |
| :--- | :--- | :--- |
| **1. Dor / Problema Central** | Documentações técnicas essenciais para capacitação em TI são densas, pouco didáticas e demoram semanas para serem adaptadas manualmente para diferentes níveis de senioridade. | ✅ Confirmado (Edital & Equipe) |
| **2. Job-to-be-Done (O que resolve a vida do usuário agora)** | *"Quando recebo um manual técnico extenso (ex.: OCI VCN ou Machine Learning), quero transformá-lo em minutos em flashcards, tutorial ou quiz no meu nível atual, com garantia de que o conteúdo é fiel ao documento original."* | ✅ Confirmado |
| **3. Processo Sem IA vs. Com IA** | **Sem IA:** Leitura linear manual -> fichamento -> criação manual de perguntas/resumos (horas/dias).<br>**Com MentorIA Tech:** Upload do documento -> seleção de Perfil/Formato/Nicho -> recuperação RAG + geração validada (segundos). | ✅ Implementado no Pipeline |
| **4. Dados de Entrada (Inputs)** | Documento técnico único (`.pdf`, `.md`, `.txt`) + Metadados de personalização (`perfil`, `formato`, `nicho`, `nivel`, `quantidade_itens`). | ✅ PDF na `main` / 🔄 `.md` e `.txt` no PR #40 |
| **5. Inteligência & Modelos (Core AI)** | • Embeddings: `gemini-embedding-001`<br>• Vector Store: `ChromaDB` (`k=10`)<br>• Reranker: `gemini-2.5-flash` (`top_n=5`)<br>• LLM Principal: Google Gemini (`temperature=0.2`, JSON mime-type)<br>• LLM Fallback: Groq (`openai/gpt-oss-120b`) | ✅ Implementado |
| **6. Guardrails, Segurança e LGPD** | • Tratamento do documento como dado não confiável (mitigação de *Prompt Injection* no system prompt).<br>• Validação determinística de `chunk_ids` e páginas no Pydantic v2.<br>• Proibição de coleta de nome, e-mail ou IP no banco (`database.py`); uso de pseudonimização SHA-256.<br>• Credenciais isoladas em variáveis de ambiente / OCI Vault. | ✅ Implementado |
| **7. Saídas & Entregáveis (Outputs)** | Pacote estruturado `PacoteFinal` (JSON) contendo `metadados`, `conteudo_adaptado` (1 dos 6 formatos), `avaliacao_qualidade` e `armazenamento_oci`. | ✅ Implementado |
| **8. Métricas de Sucesso (KPIs)** | • **Técnicas:** Latência por etapa (`duracao_ms`), taxa de JSON válido (100% pós-validação), taxa de acionamento de fallback.<br>• **Qualidade RAG:** Precision, Recall, NDCG, MRR e Hit Rate (benchmark) + verificação estrutural de referências.<br>• **Produto/Pedagógicas:** Taxa de acerto em Quizzes, tempo médio de resposta e avaliação de utilidade (feedback). | ✅ Estrutura pronta / 🔄 Coleta de feedback em integração |
| **9. Limites & Evolução (Pós-MVP)** | Integração futura com **Power BI** (a partir dos CSVs/tabelas já modeladas), bot no **Telegram**, compartilhamento via **QR Code** para testes universitários em massa e suporte multilíngue (ES/EN). | 🚀 Pós-MVP (Backlog) |
