# MentorIA Tech — Equipe 26 (Hackathon ONE G10)
*Atualizado em: 12/11/2026 — Responsável: Lídia Moura (Líder Técnica)*

## 1. Nome do Projeto
**MentorIA Tech** *(codinome de desenvolvimento: NovaMente)* — Sistema Inteligente de Adaptação e Geração de Conteúdo Educacional Técnico.

## 2. Problema
Documentações técnicas (manuais de software, guias de nuvem e artigos de engenharia) são densas, extensas e repletas de jargões, exigindo semanas de especialistas para serem adaptadas em materiais didáticos para diferentes níveis de conhecimento. O uso direto de LLMs sem recuperação ancorada gera alucinações e perda de rastreabilidade das fontes originais.

## 3. Solução
Plataforma baseada em **RAG (Retrieval-Augmented Generation)** e **IA Generativa** que recebe um documento técnico (`.pdf`, `.md` ou `.txt`) e gera automaticamente pacotes educacionais personalizados em **PT-BR** conforme:
- **Perfil do destinatário:** `Iniciante`, `Jr/Pleno`, `Arquiteto`, `Gestor`
- **Formato pedagógico de saída:** `Tutorial`, `Flashcards`, `Quiz`, `TL;DR`, `Roteiro`, `Resumo`
- **Foco Estratégico do MVP (Nicho Tecnológico):** Especializado exclusivamente no setor de **Educação em Tecnologia e Engenharia de Software**.  
  *Justificativa do nicho:* Embora o edital tenha sugerido dispersão em múltiplos nichos (Fintech, Saúde, etc.), a equipe decidiu estrategicamente concentrar 100% do MVP na área técnica. Essa decisão elimina ruídos terminológicos no RAG, aprofunda a fidelidade conceitual e direciona a solução diretamente à nossa persona-alvo do Demo Day: estudantes de tecnologia e profissionais em transição de carreira (ecossistema ONE, Alura e NoCountry).

Todos os itens gerados citam `chunk_ids` e páginas reais do documento, garantindo fidelidade técnica e rastreabilidade das fontes.

## 4. Público Prioritário
Estudantes de tecnologia, profissionais em transição de carreira, desenvolvedores (Júnior/Pleno), lideranças técnicas (Tech Leads/Arquitetos), executivos e plataformas EdTech/treinamento corporativo.

## 5. Tecnologia Principal

### Pipeline RAG
- **Extração multi-formato:** `pdfplumber` para PDFs, leitura nativa para `.md` e `.txt`
- **Segmentação (Chunking):** LangChain Text Splitters (`chunk_size=2000`, `overlap=200`)
- **Embeddings:** `gemini-embedding-001`
- **Vector Store:** ChromaDB (busca semântica por similaridade)
- **Validação:** Pydantic v2 com contratos estritos — verificação determinística de `chunk_ids` e páginas

### Orquestração de LLMs
- **Provedor principal:** Google Gemini (`gemini-3.8-flash`)
- **Fallback automático:** Groq (`openai/gpt-oss-120b`)
- **Pool de chaves:** Rotação automática entre múltiplas chaves por provedor para alta disponibilidade

### Integração OCI (Always Free)
- **Compartimento:** `mentoria-tech`
- **Bucket:** `mentoria-tech-artifacts` — armazena os JSONs de conteúdo gerado
- **Saída JSON estruturada** com campo `armazenamento_oci` (requisito NoCountry):
```json
{
  "status": "sucesso",
  "metadados": {
    "perfil_aplicado": "Iniciante",
    "formato_gerado": "Flashcards",
    "tempo_estimado_estudo_minutos": 10,
    "conceitos_chave": ["RAG", "embeddings", "chunk"]
  },
  "conteudo_adaptado": { "...": "..." },
  "avaliacao_qualidade": {
    "ancoragem_fonte_score": 0.95,
    "observacoes": ["Referências de chunks/páginas verificadas estruturalmente."]
  },
  "armazenamento_oci": {
    "bucket": "mentoria-tech-artifacts",
    "objeto_id": "resultado_20261112T010000Z.json",
    "status_upload": "concluido"
  }
}
```

### Interface e Persistência
- **Interface:** Streamlit — jornada em 4 telas (upload → configuração → geração → resultado)
- **Banco local:** SQLite com tabelas `geracoes`, `respostas`, `eventos_estudo` (telemetria anonimizada SHA-256)
- **Exportação BI:** CSVs automáticos em `data/bi_exports/` para conexão com Power BI

### Linguagem e ambiente
- **Python:** 3.11+
- **Dependências:** `oci>=2.110.0`, `pydantic>=2`, `pdfplumber`, `chromadb`, `langchain`, `streamlit`, `google-genai`, `groq`

## 6. Cenários de Demonstração (mínimo exigido: 3)

**Cenário 1 — Iniciante + Flashcards**
> Documento: `rag/Machine_Learning.pdf`
> Perfil: Iniciante · Formato: Flashcards · Nicho: Geral
> Resultado esperado: 10 flashcards com frente/verso, conceitos básicos de ML, cada um com referência de página e chunk.

**Cenário 2 — Jr/Pleno + Tutorial passo a passo**
> Documento: `rag/Machine_Learning.pdf`
> Perfil: Jr/Pleno · Formato: Tutorial · Nicho: Geral
> Resultado esperado: Tutorial com passos numerados, código ou comandos quando aplicável, fontes por passo.

**Cenário 3 — Arquiteto + Quiz com justificativas**
> Documento: `rag/Machine_Learning.pdf`
> Perfil: Arquiteto · Formato: Quiz · Nicho: Geral
> Resultado esperado: 5 questões de múltipla escolha com alternativas plausíveis, índice correto, explicação detalhada e referência de chunk/página por questão.

## 7. Infraestrutura OCI Configurada (Always Free)

| Recurso | Nome | Tipo | Status |
|---|---|---|---|
| Compartimento | `mentoria-tech` | — | ✅ Ativo |
| Grupo | `mentoria-tech-adm` | IAM Group | ✅ Criado |
| Grupo | `mentoria-tech-dev` | IAM Group | ✅ Criado |
| Grupo | `mentoria-tech-bi` | IAM Group | ✅ Criado |
| Grupo | `mentoria-tech-viewer` | IAM Group | ✅ Criado |
| Policies | Vinculadas aos grupos | IAM Policy | ✅ Criadas |
| Bucket principal | `mentoria-tech-artifacts` | Object Storage Standard | ✅ Ativo (Private) |
| Bucket documentos | `mentoria-tech-documents` | Object Storage Standard | ✅ Ativo (Private) |
| Bucket observabilidade | `mentoria-tech-observability` | Object Storage Standard | ✅ Ativo (Private) |

> ⚠️ **Nota de Governança sobre o OCI Vault:** O cofre de senhas (OCI Vault) está registrado no roadmap **Pós-MVP / Pós-Hackathon** devido ao limite técnico da camada gratuita Always Free (1 Vault por tenancy já alocado em projeto anterior). No MVP oficial, o gerenciamento seguro de credenciais é garantido via variáveis de ambiente com rotação automática de pool (`.env` local e Streamlit Secrets criptografados), mantendo `USE_OCI_VAULT=false`.

## 8. Resultado Esperado
Reduzir de semanas para menos de 60 segundos a criação de materiais de estudo técnicos validados, entregando saídas JSON estruturadas com verificação determinística de citações (`chunk_ids` e páginas), armazenamento automático na OCI e alta disponibilidade via fallback de LLMs.

## 9. Status Atual do MVP (13/11/2026)

| Componente | Status |
|---|---|
| Pipeline RAG completo (chunking, embeddings, vector store) | ✅ Implementado |
| Geração nos 6 formatos com Gemini + fallback Groq | ✅ Implementado |
| Pool de chaves com rotação automática | ✅ Implementado |
| Validação Pydantic v2 com verificação de chunks/páginas | ✅ Implementado |
| Extrator multi-formato PDF/MD/TXT | ✅ Implementado (PR #40) |
| Interface Streamlit 4 telas | ✅ Implementado (PR #42) |
| Persistência SQLite com telemetria anonimizada | ✅ Implementado |
| Integração OCI Object Storage (upload JSON) | ✅ Implementado (`services/oci_storage.py`) |
| Fallback local automático (OCI indisponível) | ✅ Implementado |
| Exportação CSV para Power BI | ✅ Implementado (`services/bi_exporter.py`) |
| Benchmark experimental (200 combinações) | ✅ Implementado |
| Testes QA automatizados (pytest) | ✅ Implementado (16 cenários em `tests/test_qa_pipeline.py`) |
| Notebook de validação (3 cenários demo) | ✅ Implementado (`rag/notebooks/validacao_pipeline_mentoria_tech.ipynb`) |

## 10. Responsável e Equipe

**Responsável pelo documento:** Lídia Moura (Lidi) — Líder Técnica  
**Equipe:** Equipe 26 — Hackathon ONE G10 (Oracle Next Education & Alura / NoCountry)
