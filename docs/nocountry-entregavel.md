# MentorIA Tech — Equipe 26 (Hackathon ONE G10)

## 1. Nome do Projeto
**MentorIA Tech** *(codinome de desenvolvimento: NovaMente)* — Sistema Inteligente de Adaptação e Geração de Conteúdo Educacional Técnico.

## 2. Problema
Documentações técnicas (manuais de software, guias de nuvem e artigos de engenharia) são densas, extensas e repletas de jargões, exigindo semanas de especialistas para serem adaptadas em materiais didáticos para diferentes níveis de conhecimento. Já o uso direto de LLMs sem recuperação ancorada gera alucinações e perda de rastreabilidade das fontes originais.

## 3. Solução
Plataforma baseada em **RAG (Retrieval-Augmented Generation)** e **IA Generativa** que recebe um documento técnico (`.pdf`, `.md` ou `.txt`) e gera automaticamente pacotes educacionais personalizados em **PT-BR** conforme o **Perfil** (`Iniciante`, `Jr/Pleno`, `Tech Lead/Arquiteto`, `Executivo/Gestor`), o **Formato Pedagógico** (`Tutorial`, `Flashcards`, `Quiz`, `TL;DR`, `Roteiro`, `Resumo`) e o **Nicho** (`Geral`, `Fintech`, `Saúde`, `E-commerce`), garantindo que 100% dos itens citem páginas e trechos reais do documento.

## 4. Público Prioritário
Estudantes de tecnologia, profissionais em transição de carreira, desenvolvedores (Júnior/Pleno), lideranças técnicas (Tech Leads/Arquitetos), executivos e plataformas EdTech/treinamento corporativo.

## 5. Tecnologia Principal
- **Linguagem e Validação:** Python 3.11+ e Pydantic v2 (contratos JSON estritos).
- **Pipeline RAG:** LangChain Text Splitters (`chunk_size=2000`, `overlap=200`), Embeddings (`gemini-embedding-001`), Vector Store (`ChromaDB`) e Reranker (`gemini-2.5-flash`).
- **LLMs (Orquestração e Fallback):** Google Gemini (provedor principal) e Groq (`openai/gpt-oss-120b` como fallback automático).
- **Interface e Persistência:** Streamlit (jornada em 4 telas), SQLite local (telemetria anonimizada SHA-256 e exportação CSV) e integração planejada com **Oracle Cloud Infrastructure (OCI Object Storage Always Free)**.

## 6. Resultado Esperado
Reduzir de semanas para menos de 60 segundos a criação de materiais de estudo técnicos validados, entregando saídas JSON estruturadas com verificação determinística de citações (`chunk_ids` e páginas) e alta disponibilidade.

## 7. Status Atual do MVP
- **Implementado na `main`:** Pipeline RAG completo, geração nos 6 formatos com Gemini + fallback Groq, validação Pydantic v2, persistência SQLite, benchmark experimental (200 combinações avaliadas) e interface Streamlit em 4 telas.
- **Em revisão / Integração final:** Extrator multi-formato `.pdf/.md/.txt` (PR #40), conexão direta entre a interface Streamlit e o módulo `rag/pipeline/` e persistência ativa no bucket OCI Object Storage Always Free.

## 8. Responsável e Atualização
- **Responsável:** Lídia Moura (Lidi) — Líder Técnica (em nome da Equipe 26 — Hackathon ONE G10).
- **Data da última atualização:** 09/11/2026.
