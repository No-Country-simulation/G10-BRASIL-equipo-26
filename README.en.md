<p align="center">
  <img src="./assets/Logomarca_principal.png" alt="MentorIA Tech logo" width="380">
</p>

<p align="center">
  🌎 <a href="./README.md">Português (PT-BR)</a> · <a href="./README.es.md">Español</a> · <strong>English</strong>
</p>

# MentorIA Tech · Hackathon ONE G10 · Team 26

> **An intelligent system that adapts technical documentation into educational content, grounded in real sources through RAG.**
> *Learning with clarity, lightness and autonomy.*

<p align="center">
  <img src="https://img.shields.io/badge/status-MVP%20Live%20%26%20Validated-brightgreen" alt="Status: MVP Live and Validated">
  <img src="https://img.shields.io/badge/Hackathon-ONE%20G10-blue" alt="Hackathon ONE G10">
  <img src="https://img.shields.io/badge/Generative%20AI-RAG%20%2B%20LLM-purple" alt="Generative AI and RAG">
  <img src="https://img.shields.io/badge/Cloud-OCI%20Always%20Free-red" alt="OCI">
  <img src="https://img.shields.io/badge/MVP%20language-PT--BR-brightgreen" alt="PT-BR">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT">
</p>

> **Live MVP (Streamlit Cloud):** [https://mentoria-tech.streamlit.app/](https://mentoria-tech.streamlit.app/)

---

## About the project

**MentorIA Tech** *(initial codename: NovaMente)* is **Team 26**'s solution for **Hackathon ONE G10**, promoted by **Oracle Next Education (ONE)** and **Alura** in partnership with **NoCountry**.

The platform takes technical documentation (a manual, a cloud guide, an article) and turns it into structured study material, personalized by **profile**, **pedagogical format** and **depth level**. It uses **RAG (Retrieval-Augmented Generation)**, LLMs with fallback and contract validation with **Pydantic v2**. The final output is persisted in **OCI Object Storage (Always Free)**.

<p align="center">
  <img src="./assets/Mascote-fundo_branco.png" alt="MentorIA Tech mascot" width="180">
</p>

### Problem
Technical documentation is dense and full of jargon. Adapting it by hand for different audiences takes weeks, and using an LLM without context control causes hallucinations and loses source traceability.

> **Guiding question:** how can complex technical documentation become accessible, personalized and structured educational content in minutes, without losing fidelity to the original sources?

### Priority audience
1. **Technology students and career-transition professionals** (primary focus).
2. **Junior/Mid developers and Tech Leads**, who need technical summaries with traceable pages and passages.
3. **Executives and EdTech/training platforms**, who need quick views (`TL;DR`, `Summary`).

---

## MVP proposal

The MVP processes **one document per run**, in **PT-BR** (the MVP's mandatory language). This English version is a complementary one, for presentations.

| Parameter | Options |
| :--- | :--- |
| **Document** | `.pdf` (with text), `.md`, `.txt` |
| **Profile** | `Iniciante` (Beginner) · `Jr/Pleno` (Junior/Mid) · `Tech Lead` · `Executivo` (Executive) |
| **Format** | `Tutorial` · `Flashcards` · `Quiz` · `TL;DR` · `Roteiro` (Script) · `Resumo` (Summary) |
| **Level** | `basic` · `intermediate` · `advanced` |

> **Decision from the 09/11/2026 meeting:** the `nicho` (niche) field is being deprecated, with a 100% focus on technology education. The `Arquiteto` and `Gestor` profiles are being renamed `Tech Lead` and `Executivo`; the code still uses the old names (see [Status](#-actual-feature-status)).

Every generated item cites **real pages and chunks** from the document, and the system verifies those references deterministically before accepting a response.

---

## Architecture

<p align="center">
  <img src="./assets/novamente_architecture_flowchart.png" alt="MentorIA Tech architecture flowchart" width="850">
</p>

```mermaid
flowchart TD
    A([PDF / MD / TXT document]) --> B[Extraction and cleaning<br/>rag/ingestao.py]
    B --> C[Chunking 2000 / overlap 200]
    C --> D[Embeddings gemini-embedding-001]
    D --> E[(In-memory ChromaDB)]
    E --> F[Top-K = 10]
    F --> G[Reranking → Top 5]
    G --> H{LLM orchestration}
    H -->|Primary| J[Groq]
    H -->|Fallback| I[Google Gemini]
    J --> K[Pydantic v2 validation + source check]
    I --> K
    K --> L([Final JSON package])
    L --> M[(Local SQLite)]
    L -.->|In integration| N[(OCI Object Storage)]
```

**RAG parameters** (chosen via a 200-combination benchmark: 40 configurations × 5 documents): `chunk_size=2000`, `overlap=200`, `K=10`, `top_n=5`.

---

## Technologies

| Layer | Technologies |
| :--- | :--- |
| **Language and contracts** | Python 3.11+ · Pydantic v2 |
| **Extraction** | `pdfplumber` (multi-format, with tables) · `pypdf` |
| **RAG** | LangChain · ChromaDB · `gemini-embedding-001` |
| **LLMs** | Groq `openai/gpt-oss-120b` (primary) · Google Gemini (fallback + embeddings/reranking) |
| **Persistence & Privacy** | Local SQLite with anonymous UUID (`usuario_id` to recover Quizzes/progress via `?uid=` or sidebar; `sessao_id` per visit — Zero PII) · OCI Object Storage |
| **Interface** | Streamlit, with Brandbook UX/UI v1.1 (WCAG AA) |
| **Cloud** | Oracle Cloud Infrastructure (OCI SDK), Always Free tier |

---

## Actual feature status

| Status | Item |
| :--- | :--- |
|  **VALIDATED** | RAG + LLM pipeline with fallback (`Groq` / `Google Gemini`) |
|  **VALIDATED** | Pydantic v2 contracts (6 formats), `nicho` removed, and source verification |
|  **VALIDATED** | FastAPI (`rag/main.py`, contract `v0.3`) and SQLite persistence (Zero PII) |
|  **VALIDATED** | Multi-format `.pdf/.md/.txt` extractor (PR #40) and RAG benchmark (200 experiments) |
|  **VALIDATED** | Live Streamlit UI ([mentoria-tech.streamlit.app](https://mentoria-tech.streamlit.app/)) with Lighthouse/Core Web Vitals optimizations (PR #51) |
|  **VALIDATED** | API key pool (`GEMINI_API_KEYS`, `GROQ_API_KEYS`) with automatic rotation |
|  **VALIDATED** | Real structured JSON upload to private OCI bucket (`mentoria-tech-artifacts`, Always Free) |
|  **VALIDATED** | Automated QA suite (`30` passing tests), trilingual QA reports & BI notebooks |
|  **POST-MVP** | OCI Vault (Always Free limit), live Power BI, Chrome Extension, Telegram Bot, OCR, EN/ES UI |

Details in [`docs/decisoes-e-status.md`](./docs/decisoes-e-status.md) *(in Portuguese)*.

---

## Demo scenarios

1. **Tutorial** · *Beginner* · `rag/Machine_Learning.pdf`: step-by-step on datasets, learning types and cross-validation, with page citations.
2. **Flashcards** · *Beginner* · *VCN networking on OCI*: cards about VCNs, subnets, gateways and security lists.
3. **Quiz** · *Junior/Mid* · `rag/Machine_Learning.pdf`: multiple-choice questions with immediate feedback and explanation.

---

## Running locally

> Windows (PowerShell). On Linux/macOS, activate with `source .venv/bin/activate`.

```powershell
git clone https://github.com/No-Country-simulation/G10-BRASIL-equipo-26.git
cd G10-BRASIL-equipo-26

py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**Environment variables:** copy the template and fill it in locally only. `rag/.env` is in `.gitignore` and **must never be pushed to GitHub**.

```powershell
Copy-Item .\rag\.env.example .\rag\.env
```
```dotenv
GEMINI_API_KEY=
GROQ_API_KEY=
```

**Interface (works without keys, using preloaded scenarios):**
```powershell
streamlit run app/main.py
```
Open `http://localhost:8501`.

**Real pipeline (requires keys):**
```powershell
python .\rag\teste_integracao.py .\rag\Machine_Learning.pdf
```

---

## Oracle Cloud (OCI)

The MVP uses the **Always Free** tier only, with the `mentoria-tech` compartment, least-privilege groups and policies, and **private** buckets. The structured JSON output is the mandatory persistence requirement. No credential is ever versioned: use environment variables, the `~/.oci/config` file (outside the repository) or OCI Vault.

Guides *(in Portuguese)*: [`docs/oci-tutorial.md`](./docs/oci-tutorial.md) · [`docs/integracao-oci.md`](./docs/integracao-oci.md)

---

## Documentation (`docs/`)

| Document | Content |
| :--- | :--- |
| [`tutorial-uso-mvp.md`](./docs/tutorial-uso-mvp.md) | Step-by-step MVP user tutorial (based on Trupeer guide) |
| [`pitch.md`](./docs/pitch.md) | Pitch and AI Canvas |
| [`arquitetura-mvp.md`](./docs/arquitetura-mvp.md) | Modules, contracts and integration |
| [`integracao-oci.md`](./docs/integracao-oci.md) | IAM, Object Storage, Vault and Autonomous Database |
| [`oci-tutorial.md`](./docs/oci-tutorial.md) | Step-by-step OCI tutorial |
| [`qa-plano.md`](./docs/qa-plano.md) | QA plan and STAR method |
| [`relatorio-qa-evidencias.en.md`](./docs/relatorio-qa-evidencias.en.md) | Final QA, BI Analyst & runtime evidence report |
| [`data_science/relatorio_qa_bi_mentoria_tech.ipynb`](./data_science/relatorio_qa_bi_mentoria_tech.ipynb) | Colab-ready QA & BI analytics notebook (`pandas`, `seaborn`, `matplotlib`) |
| [`data_science/validacao_pipeline_mentoria_tech.ipynb`](./data_science/validacao_pipeline_mentoria_tech.ipynb) | End-to-end validation notebook (3 demo scenarios) |
| [`metricas-kpis.md`](./docs/metricas-kpis.md) | Metrics, KPIs and BI model |
| [`decisoes-e-status.md`](./docs/decisoes-e-status.md) | Decisions and actual status |
| [`engenharia-prompts-e-mercado.md`](./docs/engenharia-prompts-e-mercado.md) | Prompts per profile/format and market analysis |
| [`nocountry-entregavel.md`](./docs/nocountry-entregavel.md) | MVP document for NoCountry (≤ 10,000 characters) |
| [`guia-github-projects.md`](./docs/guia-github-projects.md) | GitHub Projects sync guide |
| [`atas/`](./docs/atas/) | Sanitized meeting minutes (LGPD) |

---

## Team 26

Official roles as registered on NoCountry, alongside actual contributions to the project.

| Member | NoCountry role | Role in the project | Links |
| :--- | :--- | :--- | :--- |
| **Lídia Moura** | BI Analyst | Tech lead, OCI setup, QA and documentation | [LinkedIn](https://www.linkedin.com/in/lidimoura) |
| **Andrea De Nardi Gonzalez** | Data Analyst | Compliance and Scrum Master | [GitHub](https://github.com/AndreaGonzalez-cursoimersao) |
| **Rodrigo Silva do Carmo** | Data Scientist | RAG/LLM architecture, Pydantic contracts, benchmark | [LinkedIn](https://www.linkedin.com/in/rodrigo-do-carmo-1b7b41204/) |
| **Wagner Julio de Campos** | Full Stack Developer | Streamlit front-end and integration | [LinkedIn](https://www.linkedin.com/in/wagnercampos5/) |
| **Josiane da Silva** | Full Stack Developer | Full stack | — |
| **Marcos Vinicius Ferreira de Oliveira** | Backend Developer | Back-end, ingestion and document extraction | [GitHub](https://github.com/fervinicius) |
| **Lysara Jacó Pinheiro** | Data Analyst | Brand, Brandbook, UX/UI and marketing | [LinkedIn](https://www.linkedin.com/in/lysara-pinheiro) |
| **Vagner Marques de Souza Lopes** | Data Analyst | Data, schemas and integration | [LinkedIn](https://www.linkedin.com/in/vagnermarques-dados) |
| **Leonardo Santos** | Data Analyst | Data and document extraction | [LinkedIn](https://www.linkedin.com/in/souleosantos) |
| **João Okuyama** | Data Analyst | Data and GitHub administration | — |

---

## Transparency on AI use

The documentation, test structure and organization of this repository were supported by the Antigravity tool (AI assistant) as a productivity instrument. All generated content was produced under **the supervision, governance and review of Lídia Moura** (Tech Lead). Product decisions, experiments and validations were carried out and approved by Team 26.

---

## License

[MIT](./LICENSE) · Last updated: 12/11/2026 · Owner: Lídia Moura (Tech Lead).

