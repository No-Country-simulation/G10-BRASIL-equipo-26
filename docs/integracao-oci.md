# Proposta de Integração e Governança OCI — MentorIA Tech

**Responsável:** Lídia Moura (Lidi) — Líder Técnica  
**Data da última atualização:** 09/11/2026  
**Status:** `PROPOSTA ARQUITETURAL E PLANEJAMENTO CONTROLADO` (Nenhuma alteração em produção deve ser executada sem auditoria prévia e confirmação explícita)

---

## 1. Princípios de Governança e Segurança na OCI

1. **Conformidade Always Free:** Todos os recursos utilizados pelo projeto **MentorIA Tech** no Hackathon ONE G10 devem operar estritamente dentro da camada **Always Free** da Oracle Cloud Infrastructure (OCI), evitando qualquer geração de custo monetário.
2. **Princípio do Menor Privilégio (Least Privilege):**
   * **Proibido** conceder acesso ao projeto para o grupo padrão `All Domain Users`.
   * **Proibido** manter integrantes de desenvolvimento/BI no grupo global `Administrators` da Tenancy.
   * **Proibido** utilizar políticas amplas como `allow group ... to manage all-resources in tenancy`.
   * Todas as *Policies* devem ficar estritamente restritas ao compartimento `mentoria-tech`.
3. **Zero Credenciais no Código:** Nenhuma chave de API, OCID sensível, senha de banco, arquivo de *wallet* (`.sso`, `.p12`, `.ora`, `.pem`) ou token deve ser gravado no repositório Git. Tudo deve ser injetado via variáveis de ambiente ou lido em tempo de execução a partir do **OCI Vault**.
4. **Privacidade e LGPD (Zero PII em Object Keys):** Nenhum nome de objeto (*object key*) nos buckets ou registro no banco pode conter nome completo, e-mail, CPF ou IP de usuários. Utilizam-se apenas UUIDs (`run_id`, `document_id`) e hashes SHA-256 (`usuario_id`).

---

## 2. Matriz de Planejamento e Controle de Recursos OCI (Fase 4)

Antes da criação ou alteração de qualquer recurso na console OCI ou via CLI, aplica-se a matriz de governança abaixo:

| Recurso | Ação Planejada | Escopo | Grupo / Responsável | Risco | Plano de Reversão (Rollback) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Compartimento `mentoria-tech`** | Verificar existência / isolar todos os recursos do projeto | Tenancy Root -> `mentoria-tech` | `Administrators` (Líder Técnica / Owner da Tenancy) | Baixo (isolamento lógico) | Mover recursos ou desativar compartimento se vazio |
| **Grupo `mentoria-tech-adm`** | Criar/manter grupo para gestão exclusiva da infraestrutura do compartimento | IAM Identity Domain | Lídia Moura / Wagner Campos | Baixo | Remover membros e excluir grupo no Identity Domain |
| **Grupo `mentoria-tech-dev`** | Criar grupo para desenvolvedores (acesso a Object Storage, leitura de secrets e uso de ADB de dev) | IAM Identity Domain | Equipe Back-end / RAG / Full-stack | Baixo | Revogar associação de usuários ao grupo |
| **Grupo `mentoria-tech-bi`** | Criar grupo restrito à leitura e consulta de métricas e exportações analíticas | IAM Identity Domain | Equipe Produto / Data / BI | Mínimo (somente leitura) | Remover grupo e policy associada |
| **Grupo `mentoria-tech-viewer`** | Criar grupo opcional para inspeção visual sem permissão de escrita ou leitura de segredos | IAM Identity Domain | Convidados / QA visual | Mínimo (somente `inspect`/`read` de metadados) | Remover grupo e policy associada |
| **Policy `mentoria-tech-iam-policy`** | Aplicar políticas de menor privilégio restritas ao compartimento `mentoria-tech` | Compartimento `mentoria-tech` | `mentoria-tech-adm` | Médio (erro de sintaxe pode bloquear acesso dev) | Editar/remover statements específicos na Policy via Console |
| **Buckets Object Storage (3 buckets)** | Criar buckets privados: `mentoria-tech-documents`, `mentoria-tech-artifacts`, `mentoria-tech-observability` | Compartimento `mentoria-tech` (Standard / Always Free) | `mentoria-tech-adm` | Baixo (cota Always Free = 20 GB combinados) | Excluir objetos de teste e remover o bucket |
| **OCI Vault (`mentoria-tech-vault`)** | Criar cofre virtual (modo não pago/dentro da franquia ou Free Tier) e Master Encryption Key (Software-protected) para guardar secrets | Compartimento `mentoria-tech` | `mentoria-tech-adm` | Médio (chaves HSM têm limite/custo após trial; usar **Software Protection Mode** se aplicável ou variáveis `.env` locais se sem cota) | Agendar exclusão do secret/vault e alternar `SECRET_PROVIDER=env` |
| **OCI Autonomous Database (ADB)** | Inventariar instância existente Always Free (ATP/ADW) e criar tabelas de metadados/feedback sem `DROP`/`TRUNCATE` | Compartimento `mentoria-tech` | `mentoria-tech-adm` / Rodrigo Silva | Médio (alteração de schema) | Executar apenas `CREATE TABLE IF NOT EXISTS`; manter fallback em SQLite local |

---

## 3. Especificação de Grupos e Policies (IAM)

### 3.1. Estrutura de Grupos Proposta
* **`mentoria-tech-adm`:** Administradores da infraestrutura do projeto (gerenciam buckets, vault, banco e redes exclusivamente dentro do compartimento `mentoria-tech`).
* **`mentoria-tech-dev`:** Desenvolvedores que integram a aplicação (lêem/gravam objetos nos buckets do projeto, lêem `secret-bundles` de desenvolvimento no Vault e conectam na aplicação).
* **`mentoria-tech-bi`:** Analistas de Dados e BI (lêem apenas objetos de métricas/exportação e consultam visões analíticas).
* **`mentoria-tech-viewer`:** Acesso de inspeção restrita da arquitetura na console OCI.

### 3.2. Declarações da Policy (`mentoria-tech-policy` no compartimento `mentoria-tech`)
```text
# 1. Administração restrita ao compartimento mentoria-tech (NUNCA na tenancy inteira)
Allow group mentoria-tech-adm to manage object-family in compartment mentoria-tech
Allow group mentoria-tech-adm to manage vaults in compartment mentoria-tech
Allow group mentoria-tech-adm to manage keys in compartment mentoria-tech
Allow group mentoria-tech-adm to manage secret-family in compartment mentoria-tech
Allow group mentoria-tech-adm to manage autonomous-database-family in compartment mentoria-tech

# 2. Desenvolvimento (Object Storage + leitura de Secrets de aplicação)
Allow group mentoria-tech-dev to manage objects in compartment mentoria-tech where any {target.bucket.name='mentoria-tech-documents', target.bucket.name='mentoria-tech-artifacts', target.bucket.name='mentoria-tech-observability'}
Allow group mentoria-tech-dev to read buckets in compartment mentoria-tech
Allow group mentoria-tech-dev to read secret-bundles in compartment mentoria-tech
Allow group mentoria-tech-dev to inspect autonomous-databases in compartment mentoria-tech

# 3. Business Intelligence & QA (Somente leitura de artefatos e observabilidade)
Allow group mentoria-tech-bi to read buckets in compartment mentoria-tech
Allow group mentoria-tech-bi to read objects in compartment mentoria-tech where any {target.bucket.name='mentoria-tech-artifacts', target.bucket.name='mentoria-tech-observability'}

# 4. Visualização restrita (Opcional)
Allow group mentoria-tech-viewer to inspect all-resources in compartment mentoria-tech
```

---

## 4. Arquitetura do OCI Object Storage (Requisito Obrigatório do MVP)

### 4.1. Buckets Privados Propostos
Todos os buckets devem ser criados com **Visibilidade Privada (`Private` — No Public Access)** na camada `Standard` (coberta pelos 20 GB Always Free):

1. **`mentoria-tech-documents`:** armazena os documentos técnicos brutos enviados (`.pdf`, `.md`, `.txt`).
2. **`mentoria-tech-artifacts`:** armazena os pacotes educacionais estruturados validados pelo Pydantic (`output.json`) e metadados da execução.
3. **`mentoria-tech-observability`:** armazena registros de feedback, logs sanitizados e exportações analíticas (`.csv`) para futura conexão com Power BI.

### 4.2. Convenção de Object Keys (Sem PII)
```text
# Bucket: mentoria-tech-documents
raw/{document_id}/source.pdf
raw/{document_id}/source.md
raw/{document_id}/source.txt

# Bucket: mentoria-tech-artifacts
runs/{run_id}/input-metadata.json
runs/{run_id}/output.json

# Bucket: mentoria-tech-observability
runs/{run_id}/feedback.json
exports/{YYYY-MM-DD}/metrics.csv
```

---

## 5. Gestão de Segredos no OCI Vault

Os segredos da aplicação nunca ficam no código. A proposta contempla os seguintes *Secrets* no Vault do compartimento `mentoria-tech`:

| Nome Sugerido do Secret no OCI Vault | Variável de Ambiente Equivalente (`.env`) | Finalidade |
| :--- | :--- | :--- |
| `mentoria-tech-gemini-api-keys` | `GEMINI_API_KEYS` / `GEMINI_API_KEY` | Pool de chaves do Google Gemini para rotação automática em caso de cota (`429`) |
| `mentoria-tech-groq-api-keys` | `GROQ_API_KEYS` / `GROQ_API_KEY` | Pool de chaves da Groq para o provedor de fallback (`openai/gpt-oss-120b`) |
| `mentoria-tech-adb-credentials` | `OCI_ADB_USER`, `OCI_ADB_PASSWORD`, `OCI_ADB_DSN` | Credenciais de conexão ao schema da aplicação no Autonomous Database |
| `mentoria-tech-app-config` | `OCI_NAMESPACE`, `OCI_COMPARTMENT_OCID` | Parâmetros operacionais de ambiente (dev vs. prod) |

---

## 6. Separação de Responsabilidades: Object Storage vs. Autonomous Database

### 6.1. Divisão Arquitetural
* **OCI Object Storage:** arquivos binários e payloads completos (`source.ext`, `output.json`, `feedback.json`, `metrics.csv`).
* **OCI Autonomous Database (ou SQLite local em dev):** metadados estruturados, tempos de execução, notas de ancoragem, respostas de quizzes, feedbacks de usuários e ponteiros (`bucket` + `object_key`) para os objetos armazenados no Object Storage.

### 6.2. Modelo Relacional Proposto para o Autonomous Database (6 Entidades)
Compatível com as tabelas já implementadas em `rag/database.py` (`geracoes`, `respostas`, `eventos_estudo`) e estendido para governança completa em nuvem:

1. **`generation_run`** *(equivale a `geracoes`)*:
   * `run_id` (PK), `created_at`, `user_hash`, `session_id`, `document_id`, `profile`, `format`, `niche`, `difficulty_level`, `item_count`, `estimated_study_minutes`, `llm_provider`, `llm_model`, `prompt_version`, `extraction_ms`, `retrieval_ms`, `generation_ms`, `total_ms`, `chunk_count`, `status`.
2. **`generated_artifact`**:
   * `artifact_id` (PK), `run_id` (FK -> `generation_run`), `bucket_name`, `object_key`, `content_type`, `upload_status`, `created_at`.
3. **`quality_evaluation`**:
   * `eval_id` (PK), `run_id` (FK -> `generation_run`), `grounding_score`, `grounding_method`, `valid_json` (0/1), `valid_references` (0/1), `notes`.
4. **`user_feedback`** *(nova tabela integrada ao fluxo de sessão)*:
   * `feedback_id` (PK), `run_id` (FK -> `generation_run`), `user_hash`, `session_id`, `rating` (1 a 5), `is_useful` (0/1), `comment_sanitized`, `created_at`.
5. **`quiz_interaction`** *(equivale a `respostas`)*:
   * `interaction_id` (PK), `run_id` (FK -> `generation_run`), `user_hash`, `session_id`, `round_id`, `question_index`, `question_ref_hash`, `topic_hash`, `topic`, `subtopic`, `difficulty`, `selected_option`, `is_correct` (0/1), `response_time_sec`, `attempt_number`, `created_at`.
6. **`pipeline_event`** *(equivale a `eventos_estudo` + logs de erro por etapa)*:
   * `event_id` (PK), `run_id` (FK -> `generation_run`), `user_hash`, `session_id`, `stage` (`extraction`, `retrieval`, `generation`, `validation`, `storage`, `study`), `event_type`, `error_code`, `details_json`, `created_at`.
