<p align="center">
  <img src="./app/assets/Logomarca principal/Logomarca principal.png" alt="Logomarca MentorIA-Tech" width="380">
</p>

# Hackathon ONE G10 Brasil Equipe 26 · MentorIA-Tech

> **Sistema Inteligente de Adaptação e Geração de Conteúdo Educacional**  
> *Transforme documentações técnicas densas em experiências de aprendizagem personalizadas com clareza, leveza e autonomia.*

---

## 🎯 Sobre o Projeto

O **MentorIA-Tech** é uma plataforma EdTech desenvolvida para o **Hackathon ONE G10** (parceria entre **Oracle Next Education**, **Alura** e **No Country**). A solução automatiza a conversão de manuais de software, artigos técnicos e guias de infraestrutura em materiais didáticos estruturados, utilizando arquitetura de **RAG (Retrieval-Augmented Generation)**, orquestração de **LLMs com fallback** e persistência obrigatória no **OCI Object Storage (camada Always Free)**.

### 👥 Perfis de Público Atendidos:
- **Iniciante / Transição de Carreira:** Linguagem acolhedora, analogias do dia a dia e eliminação de jargões excessivos.
- **Desenvolvedor Júnior / Pleno:** Foco prático, trechos de código, comandos de terminal e regras de implementação.
- **Líder Técnico / Arquiteto:** Visão sistêmica, trade-offs de engenharia, requisitos não funcionais e segurança.
- **Gestor / Executivo (Não Técnico):** Síntese executiva (TL;DR), impactos de negócio e métricas estratégicas.

---

## 🛠️ Tecnologias Utilizadas

- **Interface & Experiência:** [Streamlit](https://streamlit.io/) com tokens visuais e componentes do **Brandbook UX/UI v1.1** (Inter, paleta Menta, Lilás e Rosa, conformidade WCAG AA).
- **Engenharia de Dados & RAG:** [LangChain](https://www.langchain.com/), [ChromaDB](https://www.trychroma.com/) (Vector Store em memória), segmentação recursiva e geração de embeddings com `gemini-embedding-001`.
- **Orquestração de LLMs com Fallback:** Provedor primário **Google Gemini** (`gemini-2.5-flash`) com fallback automático para **Groq** (`openai/gpt-oss-120b`).
- **Validação e Contratos Estritos:** [Pydantic v2](https://docs.pydantic.dev/) para validação de schemas de entrada e saída estruturada (`PacoteFinal`).
- **Nuvem & Infraestrutura:** [Oracle Cloud Infrastructure (OCI)](https://www.oracle.com/cloud/) via `oci-sdk` utilizando a camada **Always Free** para persistência de documentos e JSONs educativos.
- **Leitura & Ingestão de Documentos:** [PyPDF](https://pypdf.readthedocs.io/) e leitores de Markdown/Texto plano.

---

## 📐 Arquitetura da Solução

<p align="center">
    <img src="./assets/novamente_architecture_flowchart.png" alt="Fluxograma da Arquitetura do Projeto MentorIA-Tech" width="850">
</p>

### Diagrama do Fluxo RAG & Orquestração Pedagógica:
```text
Documento Técnico (.pdf, .md, .txt)
                │
                ▼
       Extração de Texto (PyPDF)
                │
                ▼
   Segmentação em Chunks & Embeddings (Gemini)
                │
                ▼
     Busca Vetorial (ChromaDB) + Reranking
                │
                ▼
   Recuperação de Contexto Relevante Ancorado
                │
                ▼
   Orquestração LLM (Gemini ➔ Fallback Groq)
                │
                ▼
  Validação de Citações e Schema (Pydantic v2)
                │
                ▼
 ┌──────────────────────────────────────────────┐
 │  Interface Interativa Streamlit              │
 │  - Quiz Interativo em tempo real             │
 │  - Flashcards com dicas pedagógicas          │
 │  - Exportação Multiformato (JSON, MD, Anki)  │
 │  - Coleta de Feedback do Usuário             │
 └──────────────────────┬───────────────────────┘
                        │
                        ▼
    Persistência no OCI Object Storage (Always Free)
```

---

## 🚀 Guia de Instalação e Execução

### 1. Clonar o repositório
```bash
git clone https://github.com/No-Country-simulation/G10-Brasil-Equipe-26-NovaMente.git
cd G10-Brasil-Equipe-26-NovaMente
```

### 2. Criar e ativar o ambiente virtual Python
```powershell
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências do projeto
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar as variáveis de ambiente (Opcional para modo live API)
Copie o arquivo de exemplo em `rag/.env.example` para `rag/.env` e configure suas chaves:
```dotenv
GEMINI_API_KEY=sua_chave_gemini_aqui
GROQ_API_KEY=sua_chave_groq_aqui
```
*(Nota: O MentorIA-Tech conta com motor inteligente integrado e 3 cenários reais pré-carregados, permitindo demonstrações visuais e testes imediatos mesmo sem chaves externas configuradas).*

### 5. Iniciar a aplicação Streamlit
```bash
streamlit run app/main.py
```
Acesse no seu navegador: `http://localhost:8501`.

---

## 🎬 Demonstração Prática (Cenários Reais do Edital)

O sistema conta com 3 cenários completos de execução com documentos técnicos reais:

### 🎓 Cenário 1: Guia Prático Passo a Passo (Tutorial)
- **Documento Base:** *Fundamentos de Machine Learning e Modelos Preditivos* (`rag/Machine_Learning.pdf`).
- **Perfil do Destinatário:** *Iniciante / Transição de Carreira*.
- **Formato:** *Tutorial Didático em 5 Etapas*.
- **Resultado:** Explicação sequencial da anatomia de um dataset (linhas = instâncias, colunas = features, coluna alvo = target), tipos de aprendizado e técnicas de validação cruzada (*Cross-validation*), com 100% de citações das páginas 5, 6, 13 e 14.

### 🗂️ Cenário 2: Flashcards de Memorização
- **Documento Base:** *Introdução à Arquitetura de Redes VCN na OCI*.
- **Perfil do Destinatário:** *Iniciante / Transição de Carreira*.
- **Formato:** *Flashcards de Revisão Ativa*.
- **Resultado:** 4 cartões com perguntas conceituais, respostas analógicas e dicas didáticas sobre Redes Virtuais na Nuvem, Sub-redes Públicas vs. Privadas, Internet Gateways, NAT Gateways e Security Lists.

### 🎯 Cenário 3: Quiz Interativo com Gabarito Justificado
- **Documento Base:** *Fundamentos de Machine Learning e Modelos Preditivos*.
- **Perfil do Destinatário:** *Desenvolvedor Júnior / Pleno*.
- **Formato:** *Quiz Interativo de 4 Questões de Múltipla Escolha*.
- **Resultado:** O estudante seleciona a alternativa diretamente na interface e recebe feedback imediato de acerto ou erro, com justificativa fundamentada e tag do assunto.

---

## 👥 Integrantes da Equipe (Grupo 10 · Equipe 26)

- **Wagner Julio:** Full Stack & Frontend Developer
- **Rodrigo Silva:** Data Scientist & RAG / LLM Engineer
- **Lídia Moura:** BI Analyst & OCI Cloud Architect
- **Vinicius Ferreira:** Backend & Ingestão de Documentos
- **Marcos Vinicius:** Backend Developer
- **Lysara Jacó:** Data Analyst & UX/UI Designer
- **Leonardo Santos:** Data Analyst
- **Vagner Marques:** Data Analyst
- **João Okuyama:** Data Analyst
- **Josiane Da Silva:** Full Stack Developer
- **Andrea De Nardi:** Data Analyst

---

## 📄 Licença

Este projeto está licenciado sob os termos da licença [MIT](LICENSE).
