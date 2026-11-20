# Ata de Reunião — 19/11/2026 (Otimização LLM, Validação Local do MVP, Pitch e Cronograma Final)

**Projeto:** MentorIA Tech — Equipe 26 | Hackathon ONE G10  
**Data:** 19/11/2026  
**Classificação:** Registro público higienizado (sem PII / sem informações pessoais ou sensíveis)

---

## 1. Resumo Executivo
* **Merge do PR #52 e Ganho de Desempenho:** Rodrigo Silva realizou o merge do PR #52 (`mentoria-tech-integracao` → `main`), consolidando a priorização do **Groq** como provedor principal na geração de conteúdo (`LLM_PROVIDER_ORDER=groq,gemini`), ajuste de timeouts HTTP do Gemini (`20s` para avaliação/reranking e `30s` para geração fallback) e organização dos notebooks na pasta `data_science/`. Lídia Moura apresentou a execução local ao vivo, evidenciando a redução do tempo total de geração do Quiz para `~13,7s`.
* **Demonstração das Funcionalidades do MVP:** Lídia Moura demonstrou a ingestão multi-formato (`.pdf`, `.md`, `.txt` e texto colado com pré-visualização rápida), perfis e níveis de complexidade, Quiz interativo com tentativas múltiplas e resumo de desempenho por assunto, além das opções de download (`.json`, `.md`, `.csv` para Anki) e visualização em `TL;DR` e `Flashcards`.
* **Deploy e Chaves de API:** Wagner Campos relatou restrições de faturamento/cota nas novas chaves do Gemini para embeddings em ambiente de nuvem. A equipe alinhou evitar o uso de cartões de crédito em testes gratuitos, confirmar os critérios do edital (que aceitam execução local e vídeo de entrega caso o deploy automatizado oscile) e testar plataformas alternativas (Railway/Vercel) para conectividade do backend.
* **Modelagem Analítica e Power BI:** Lídia Moura apresentou a modelagem Star Schema a partir dos CSVs exportados (`data/bi_exports/`), incluindo a tabela `telemetria_api`, com previsão de incorporar posteriormente os feedbacks de avaliação do Streamlit em fluxo contínuo.
* **Estratégia do Pitch, Vídeo Obrigatório e Ensaios:** A equipe revisou a estrutura dos slides no Canva (Problema → Identidade/UX da marca como solução → Arquitetura & diferenciais vs. LLMs abertas/NotebookLM → Demonstração → Equipe 26 → Roadmap/QR Code), definiu os critérios do vídeo obrigatório (3 exemplos de execução, 2 perfis e 2 formatos distintos) e planejou enquetes para os ensaios gerais no aplicativo Microsoft Teams.

---

## 2. Decisões Alinhadas
1. **Priorização do Groq e Timeouts do Pipeline:** Consolidado `20s` para avaliação/reranking e `30s` para fallback de geração, mantendo **Groq (`openai/gpt-oss-120b`)** como provedor principal de geração.
2. **Validade da Execução Local e Vídeo de Backup:** Confirmado junto aos requisitos do edital que a execução local e a demonstração gravada atendem à entrega do MVP, evitando custos/cartões em nuvem e garantindo plano B para o Demo Day.
3. **Critérios do Vídeo Obrigatório (entrega até domingo 22/11):** Contemplar **3 exemplos de execução**, **2 perfis diferentes** e **2 formatos distintos**, com apoio de roteiro para locução e legendas de acessibilidade.
4. **Fluxo Oficial do Pitch (Canva):** Problema → Identidade visual & UX (leveza da proposta) → Arquitetura & Benchmark (200 experimentos + auditoria por IA) → Demo → Equipe 26 (fotos com corte circular padronizado) → Visão LATAM / QR Code.
5. **Ensaios Gerais via Microsoft Teams:** Utilizar o aplicativo instalado do Teams para estabilidade técnica nos ensaios do fim de semana/segunda-feira e gravação de backup.
6. **Avaliações de Viabilidade Futura:** Avaliar posteriormente alternativas de modelo local/aberto (ex.: Ollama) e evolução da API para Extensão do Google Chrome como validação de produto pós-MVP.

---

## 3. Ações e Próximos Passos Registrados
* **Lídia Moura:** Finalizar o dashboard Power BI a partir dos CSVs em `data/bi_exports/`, produzir os vídeos obrigatórios conforme o roteiro e critérios do edital, finalizar ajustes visuais do mascote e abrir enquete de horários para o ensaio geral.
* **Rodrigo Silva:** Enxugar os textos nos slides de Arquitetura para otimizar o tempo de fala, baixar o aplicativo do Microsoft Teams e treinar a apresentação.
* **Wagner Campos:** Testar alternativas de deploy do backend (Railway/Vercel) e separar melhorias isoladas de interface em PR específico.
* **Andrea Gonzalez:** Explicar o método STAR para reforçar o storytelling do pitch, alinhar datas de conclusão no GitHub Projects, coordenar legendas/locução acessível para o vídeo e publicar a enquete de reunião.
* **Lysara Pinheiro:** Padronizar o recorte/formato circular das fotos da equipe nos slides (sem distorção/pixelação) e apoiar nos testes visuais do mascote.
* **Toda a Equipe:** Participar dos ensaios conjuntos no fim de semana/segunda-feira e concluir as entregas e avaliações na plataforma até domingo (22/11).
