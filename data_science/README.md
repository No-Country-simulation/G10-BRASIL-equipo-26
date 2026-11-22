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

# MentorIA Tech — Previsão de Consumo e Saturação de APIs

Dois notebooks independentes do backend para analisar consumo de APIs e investigar a possível saturação das cotas Gemini/Groq.

## Arquivos

### `MentorIA_Tech_comparacao_3_modelos.ipynb`
Experimento com **dados sintéticos**, comparando três modelos Random Forest:

- **A:** Random Forest direto.
- **B:** Random Forest com ajuste de hiperparâmetros via `TimeSeriesSplit`.
- **C:** Random Forest que estima chamadas por usuário e tokens por chamada, reconstruindo os totais diários.

Usa teste cronológico, métricas de erro e **60 cenários de 30 dias** para avaliar a detecção de saturação. Simula limites de RPM, TPM e RPD e fallback entre dois projetos Gemini e Groq. As cotas são **ilustrativas**, não uma representação completa das cotas reais.

### `MentorIA_Tech_previsao_real.ipynb`
Analisa a **telemetria real** armazenada em `novamente.db`, acessado em **somente leitura**. Apresenta consumo por operação/modelo, cobertura de tokens e histórico diário.

O treinamento exploratório só é habilitado com histórico mínimo suficiente (**60 dias completos**, além de verificações de qualidade). Com dados insuficientes, mostra diagnósticos e um cenário condicional, **não uma previsão validada**. Não gera dados sintéticos.

## Como executar

1. Instale `numpy`, `pandas`, `matplotlib`, `scikit-learn` e `ipykernel`.
2. Abra os notebooks no VS Code ou Jupyter e execute as células em ordem.
3. Para analisar dados reais, coloque `novamente.db` na mesma pasta do notebook ou ajuste a variável `DB`. O notebook sintético funciona sem o banco.

## Limitações

Os resultados sintéticos **não comprovam desempenho em produção**. A previsão real depende de mais histórico, identificação de chave/projeto/modelo por tentativa e cotas efetivas atualizadas. Os cenários de crescimento de usuários são hipóteses que precisam ser validadas com dados reais, não previsões de aquisição.
