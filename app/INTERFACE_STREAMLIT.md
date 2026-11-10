# 💻 Módulo da Interface (Frontend - Streamlit)

Este diretório contém a interface interativa do **Projeto NovaMente**, construída com [Streamlit](https://streamlit.io/) para atender a todos os requisitos visuais, de parametrização e de validação do Hackathon ONE G10.

---

## 📌 O que já está implementado neste app (`app/main.py`)

A interface foi estruturada e alinhada com as especificações do documento do projeto (`G10 - Hackathon - NovaMente.pdf`):

1. **Barra Lateral de Parametrização Completa:**
   - **Perfil do Destinatário:** Iniciante / Transição, Desenvolvedor Júnior / Pleno, Líder Técnico / Arquiteto, Gestor / Executivo (Não Técnico).
   - **Formato Pedagógico:** Flashcards, Quiz Interativo, Tutorial Passo a Passo, Resumo TL;DR, Roteiro de Aula / Vídeo.
   - **Nicho / Contexto de Aplicação:** Geral, Fintech, Saúde, E-commerce.
   - **Nível de Detalhe:** Sintético, Didático, Aprofundado.

2. **Ingestão Flexível de Conteúdo Técnico:**
   - Upload de arquivos nos formatos `.pdf`, `.md` e `.txt`.
   - Alternativa de inserção direta via campo de texto bruto.
   - Campo para identificação do título ou tema do documento.

3. **Validações e Tratamento de Erros:**
   - Alertas visuais amigáveis caso o usuário tente submeter o formulário sem preencher o título ou sem carregar um documento.

4. **Renderização dos Resultados e Métricas:**
   - Cards com indicadores do RAG: Tempo de Estudo, Score de Ancoragem (Grounding / Mitigação de Alucinação), Nível de Clareza Pedagógica e Status de Persistência no OCI Bucket.
   - **Abas de Visualização:**
     - *Visualização Interativa:* Flashcards expansíveis, dicas didáticas e observações pedagógicas.
     - *JSON Estruturado:* Inspeção completa do payload de entrada e do schema de saída gerado.
     - *Persistência OCI & Download:* Botão direto para exportar o arquivo JSON adaptado e conferir os identificadores do bucket.

5. **Dados Mockados para Desenvolvimento Desacoplado:**
   - O app já conta com uma simulação do schema JSON oficial para que o frontend possa ser testado visualmente mesmo antes da conclusão dos pipelines de IA e nuvem.

---

## 🛠️ Como rodar o app localmente

Execute os passos abaixo a partir da raiz do repositório (`G10-Brasil-Equipe-26-NovaMente`):

### 1. Criar e ativar o ambiente virtual (Recomendado)
```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / Mac / WSL
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```
*(Caso queira rodar apenas a interface de imediato: `pip install streamlit`)*

### 3. Iniciar a aplicação
```bash
streamlit run app/main.py
```
O Streamlit abrirá automaticamente no navegador em: `http://localhost:8501`.

---

## 🤝 Como as outras áreas devem se conectar ao `app`

Para mantermos o código limpo, desacoplado e sem conflitos de merge, cada frente deve desenvolver seus módulos nas suas respectivas pastas. O ponto de integração no `app/main.py` está sinalizado na linha com o comentário `# TODO`.

### 1. Área: `rag/` (Engenharia de Dados e Ingestão)
* **Responsabilidade:** Criar a função que recebe o arquivo ou texto bruto, realiza a extração (PyPDF/Markdown), segmentação (chunking), geração de embeddings e busca por similaridade.
* **Como vincular ao app:**  
  Expor uma função em `rag/pipeline.py` (ou módulo equivalente):
  ```python
  from rag.pipeline import recuperar_contexto_relevante

  # No app/main.py:
  contexto = recuperar_contexto_relevante(documento_conteudo, query="...")
  ```

### 2. Área: `agents/` (Engenharia de Prompts e Orquestração LLM)
* **Responsabilidade:** Montar os prompts persona (LangChain / LangGraph), chamar o modelo (Google Gemini, OpenAI, etc.), validar a fidelidade técnica (grounding score) e estruturar a saída respeitando rigorosamente o schema JSON do projeto (`data/output_schema.json`).
* **Como vincular ao app:**  
  Expor uma função central em `agents/orquestrador.py`:
  ```python
  from agents.orquestrador import gerar_conteudo_educacional

  # No app/main.py (substituindo a variável mock):
  resposta_estruturada = gerar_conteudo_educacional(payload_entrada)
  ```

### 3. Área: `services/` (Oracle Cloud Infrastructure - OCI)
* **Responsabilidade:** Integrar com o **OCI Object Storage** (Always Free) via `oci-sdk` para salvar o documento técnico enviado e o arquivo JSON resultante.
* **Como vincular ao app:**  
  Expor funções em `services/oci_storage.py`:
  ```python
  from services.oci_storage import upload_para_bucket

  # No app/main.py:
  status_upload = upload_para_bucket(
      bucket_name="novamente-conteudos-educativos",
      objeto_id=f"conteudo-{formato_saida.lower()}.json",
      conteudo_json=resposta_estruturada
  )
  ```

### 4. Área: `api/` (Opcional - Backend REST)
* Se a equipe optar por rodar a aplicação em arquitetura desacoplada via FastAPI/Flask, o `app/main.py` fará apenas uma chamada HTTP:
  ```python
  import requests

  resposta = requests.post("http://localhost:8000/api/v1/adaptar", json=payload_entrada)
  resposta_estruturada = resposta.json()
  ```

---

## 📋 Regras de Trabalho e Boas Práticas (Git)

- **Nunca faça commits direto na branch `main`!**
- Sempre crie uma branch descritiva a partir da `main` atualizada antes de iniciar uma tarefa:
  ```bash
  git checkout main
  git pull origin main
  git checkout -b feature/nome-da-sua-tarefa
  ```
- Ao finalizar, faça o push e abra um **Pull Request (PR)** para revisão do time.