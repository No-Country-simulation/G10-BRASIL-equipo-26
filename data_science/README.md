# Data Science, Telemetria & Notebooks — MentorIA Tech

Este diretório centraliza os notebooks analíticos, de validação ponta a ponta e de auditoria de telemetria/BI do projeto **MentorIA Tech**.

## Notebooks disponíveis

| Arquivo | Finalidade |
|---|---|
| `relatorio_qa_bi_mentoria_tech.ipynb` | Análise exploratória da telemetria (`rag/novamente.db`: `geracoes`, `respostas`, `telemetria_api`), latências por etapa/provedor e gráficos estilo Colab/BI. |
| `validacao_pipeline_mentoria_tech.ipynb` | Validação ponta a ponta dos 3 cenários demo (Iniciante/Flashcards, Jr/Pleno/Tutorial, Tech Lead/Quiz), upload OCI Object Storage e exportação CSV para `data/bi_exports/`. |

## Como executar

1. A partir da raiz do repositório (`G10-BRASIL-equipo-26/`), ative o ambiente virtual `.venv`.
2. Abra qualquer notebook no VS Code / Jupyter ou Google Colab.
3. Os notebooks resolvem automaticamente o caminho raiz do projeto e leem `rag/novamente.db` e `rag/.env` (não versionados).
