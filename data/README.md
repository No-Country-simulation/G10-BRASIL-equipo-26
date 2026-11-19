# 📂 Dados & Exportações Analíticas — MentorIA Tech

Este diretório armazena artefatos de dados locais e exportações analíticas do projeto **MentorIA Tech**.

## Estrutura e uso ativo no MVP

- **`data/bi_exports/`** *(gerado em runtime)*: pasta padrão onde `services/bi_exporter.py` grava os CSVs sanitizados (`geracoes.csv`, `respostas.csv`, `eventos_estudo.csv`, `telemetria_api.csv`) para consumo em BI, e onde `services/oci_storage.py` salva o fallback local caso a OCI não esteja disponível.
- **`data/output_schema.json`** *(referência histórica/preliminar)*: esquema JSON inicial desenhado antes da definição dos contratos estritos em Pydantic v2 (`rag/pipeline/schemas.py` / contrato `v0.3`). Mantido apenas para rastreabilidade histórica.

> **Nota:** Não versione arquivos confidenciais, bancos SQLite locais (`rag/novamente.db`) ou credenciais de acesso neste diretório.
