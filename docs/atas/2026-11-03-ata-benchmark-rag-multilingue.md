# Ata de Reunião — 03/11/2026 (Benchmark RAG, Persistência SQLite, Público-Alvo e Feedback)

**Projeto:** MentorIA Tech *(codinome inicial: NovaMente)* — Equipe 26 | Hackathon ONE G10  
**Data:** 03/11/2026  
**Classificação:** Registro público higienizado (sem PII / sem transcrição integral)

---

## 1. Resumo Executivo
* **Apresentação do Benchmark Automatizado do RAG:** Rodrigo Silva apresentou os resultados de dois dias de experimentos sobre 5 arquivos PDF técnicos (82 páginas e 75 perguntas no total), testando 40 configurações e 200 combinações de `chunk_size` (500 a 2000), `overlap` (10% e 20%), `K` (5, 10, 15) e `reranking` (3 e 5), avaliando *Precision*, *Recall*, *NDCG*, *MRR* e *Hit Rate*. Foi selecionada a configuração `CHUNK_SIZE=2000`, `OVERLAP=200`, `K=10` e `TOP_N=5` pelo equilíbrio superior entre precisão e velocidade de recuperação.
* **Contratos Pydantic v2 e Persistência de Eventos/Respostas:** Demonstração dos schemas estritos e da estrutura de banco de dados contendo metadados de geração, controle de tentativas em questões de Quiz (`rodada_id`, `geracao_id`, `usuario_id`, `sessao_id`, `assunto`, `subassunto`, `dificuldade`, `acertou`, `tempo_resposta_segundos`).
* **Integração do Extrator de Documentos:** Alinhamento entre Leonardo Santos, Vinicius Ferreira e Rodrigo Silva para integrar o módulo de leitura multi-formato (`.pdf`, `.md`, `.txt`) ao pipeline RAG.
* **Foco em Estudantes de Tecnologia e Coleta de Feedback:** Consenso em direcionar a comunicação e validação para a área de tecnologia, mantendo a flexibilidade dos campos obrigatórios do edital (`perfil`, `formato`, `nicho`), além de incluir espaço para avaliação/feedback do usuário no banco de dados.

---

## 2. Decisões Alinhadas
1. **Incorporação dos parâmetros otimizados do RAG na `main`:** Adoção oficial da Configuração A selecionada no benchmark.
2. **Disponibilização dos formatos de saída:** Manter os 6 formatos estruturados (`Tutorial`, `Flashcards`, `Quiz`, `TL;DR`, `Roteiro` e `Resumo`).
3. **Arquitetura de Dados Híbrida (SQLite local -> OCI Object Storage & Autonomous DB):** Utilizar Object Storage para documentos/artefatos e banco relacional para metadados, interações de quiz e feedbacks.
4. **Atualização simultânea do GitHub Projects:** Revisar e atualizar os cartões do painel em paralelo durante as reuniões de alinhamento.
