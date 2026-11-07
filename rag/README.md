# NovaMente — RAG, LLM, Pydantic e Benchmark

## 1. Visão geral

Este diretório contém os componentes desenvolvidos para o processamento de documentos e a geração de produtos educacionais do projeto **NovaMente**.

A implementação utiliza:

- **RAG (Retrieval-Augmented Generation):** recuperação de informações relevantes de documentos.
- **LLM:** geração de conteúdo educacional utilizando Gemini como provedor principal e Groq como fallback.
- **Pydantic v2:** definição de contratos, validação e estruturação dos dados.
- **ChromaDB:** armazenamento e recuperação vetorial.
- **Benchmark:** avaliação experimental de diferentes configurações de recuperação e reranking.
- **Extração provisória:** leitura de documentos PDF utilizando `pypdf`.

A entrega foi organizada para facilitar a integração com os demais componentes desenvolvidos pela equipe.

A interface FastAPI de demonstração, o banco SQLite, as credenciais reais e os ambientes virtuais locais não fazem parte desta entrega.

---

## 2. Estrutura do projeto

```text
rag/
├── pipeline/
│   ├── schemas.py
│   ├── rag_config.py
│   ├── rag_retrieval.py
│   └── llm_pipeline.py
│
├── benchmark/
│   ├── analisar_benchmark_rag_automatico_otimizado2_corrigido.py
│   ├── analisar_benchmark_top10_5_pdfs.ipynb
│   ├── perguntas/
│   ├── analise_benchmark/
│   └── pdfs/
│
├── extrator_temporario/
│   └── extrair_pdf_teste.py
│
├── Machine_Learning.pdf
├── teste_integracao.py
├── visualizar_resultados_teste.ipynb
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

O PDF de exemplo deve ser incluído apenas se sua licença permitir redistribuição.

### Responsabilidades dos módulos

| Componente | Responsabilidade |
|---|---|
| `schemas.py` | Contratos e validação dos dados com Pydantic |
| `rag_config.py` | Configurações de chunking, embeddings e recuperação |
| `rag_retrieval.py` | Indexação, embeddings, recuperação e reranking |
| `llm_pipeline.py` | Geração de conteúdo com Gemini e fallback Groq |
| `benchmark/` | Experimentos e avaliação de configurações de RAG |
| `extrator_temporario/` | Extração provisória de texto de PDFs |
| `teste_integracao.py` | Teste completo dos componentes |
| `visualizar_resultados_teste.ipynb` | Visualização dos produtos gerados |

---

## 3. Requisitos

Para executar o projeto, são necessários:

- Python 3.11 ou superior, preferencialmente em uma versão compatível com todas as dependências.
- Acesso à internet.
- Chave de API do Gemini.
- Chave de API do Groq para fallback.
- Bibliotecas listadas em `rag/requirements.txt`.

Para executar novamente o benchmark, também será necessária uma chave da Voyage AI.

As APIs podem possuir limites gratuitos, cotas de utilização e custos associados.

---

## 4. Instalação

Todos os comandos desta seção devem ser executados a partir da **raiz do repositório `G10-BRASIL-equipo-26`**.

### 4.1. Criar o ambiente virtual

No Windows, utilizando PowerShell:

```powershell
python -m venv .venv
```

Ative o ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4.2. Instalar as dependências

```powershell
python -m pip install --upgrade pip
python -m pip install -r .\rag\requirements.txt
```

O arquivo `rag/requirements.txt` contém as dependências específicas do pipeline e do benchmark.

O `requirements.txt` localizado na raiz do repositório pertence ao projeto geral da equipe e não deve ser confundido com o arquivo deste módulo.

Recomenda-se utilizar um ambiente virtual isolado para evitar conflitos entre dependências.

### 4.3. Configurar as credenciais

Copie o arquivo de exemplo:

```powershell
Copy-Item .\rag\.env.example .\rag\.env
```

Abra `rag/.env` e preencha as credenciais e os parâmetros exigidos pelos módulos.

As principais variáveis são:

```dotenv
GEMINI_API_KEY=sua_chave_gemini
GROQ_API_KEY=sua_chave_groq

GEMINI_MODEL=gemini-3.6-flash
GROQ_MODEL=openai/gpt-oss-120b
```

Os identificadores dos modelos são exemplos da configuração utilizada no teste local. É necessário confirmar sua disponibilidade na conta e no provedor correspondente.

Para o benchmark, também será utilizada:

```dotenv
VOYAGE_API_KEY=sua_chave_voyage
```

**Segurança:** nunca envie arquivos `.env` com credenciais reais ao GitHub. O repositório deve conter apenas `.env.example`, sem chaves válidas.

---

## 5. Arquitetura do pipeline

O pipeline transforma um documento em produtos educacionais estruturados.

### 5.1. Fluxo de processamento

```text
Documento PDF
      |
      v
Extração de texto
      |
      v
DocumentoExtraido (Pydantic)
      |
      v
Segmentação em chunks
      |
      v
Embeddings Gemini
      |
      v
Indexação ChromaDB
      |
      v
Recuperação e reranking
      |
      v
Contexto relevante
      |
      v
Geração com Gemini
      |
      +---- Falha ----> Groq (fallback)
      |
      v
Validação Pydantic
      |
      v
Produto educacional estruturado
      |
      v
Arquivo JSON
```

### 5.2. Configuração de recuperação

O arquivo `rag_config.py` centraliza os parâmetros de recuperação.

Configuração utilizada no desenvolvimento:

| Parâmetro | Valor |
|---|---|
| Chunk size | 2.000 caracteres |
| Chunk overlap | 200 caracteres |
| K Retriever | 10 |
| Top N Reranker | 5 |
| Embedding | `gemini-embedding-001` |
| Reranking | `gemini-2.5-flash` |

Esses valores são parâmetros de trabalho e podem ser ajustados conforme os documentos e os resultados de novos experimentos.

### 5.3. Imports e integração

Os módulos preservam imports absolutos do projeto original, como:

```python
from schemas import ...
from rag_config import ...
```

Para integrá-los sem modificar os arquivos, a aplicação deve tornar `rag/pipeline/` acessível no caminho de imports do Python.

A equipe poderá adaptar os imports ao integrar os componentes à arquitetura definitiva do NovaMente.

É importante utilizar um único caminho de importação para cada classe Pydantic, evitando carregar o mesmo schema sob nomes de módulos diferentes.

---

## 6. Produtos educacionais

O pipeline gera seis formatos:

| Produto | Objetivo |
|---|---|
| Tutorial | Explicar o conteúdo de maneira didática |
| Flashcards | Apoiar a memorização e revisão |
| Quiz | Avaliar o conhecimento do estudante |
| TL;DR | Apresentar uma síntese curta |
| Roteiro | Organizar uma sequência de estudo ou apresentação |
| Resumo | Sintetizar os principais conceitos |

As saídas são estruturadas e validadas por contratos Pydantic.

O objetivo da validação é garantir que os dados respeitem a estrutura definida. Isso não substitui uma avaliação da correção factual ou da qualidade pedagógica do conteúdo gerado.

---

## 7. Teste de integração

O arquivo `teste_integracao.py` permite verificar o funcionamento conjunto dos componentes.

O teste utiliza um PDF real, realiza a recuperação de contexto e gera os seis produtos educacionais.

### 7.1. PDF de exemplo

O documento utilizado durante o desenvolvimento foi:

```text
rag/Machine_Learning.pdf
```

O PDF possui 16 páginas com texto extraível.

Caso esse documento não esteja incluído no repositório, utilize outro PDF com texto extraível e informe seu caminho ao executar o teste.

O extrator provisório não realiza OCR. Portanto, PDFs digitalizados sem camada de texto podem não funcionar corretamente.

### 7.2. Executar o teste

A partir da raiz do repositório:

```powershell
python .\rag\teste_integracao.py .\rag\Machine_Learning.pdf
```

O teste executa:

1. Extração do texto do PDF.
2. Criação do índice vetorial.
3. Recuperação de contexto para os formatos solicitados.
4. Geração dos seis produtos educacionais.
5. Validação dos resultados com Pydantic.
6. Armazenamento dos resultados em JSON.

O índice é reutilizado durante a geração dos seis formatos, evitando repetir desnecessariamente a indexação do documento.

### 7.3. Resultados esperados

Exemplo de saída:

```text
PDF: Machine_Learning.pdf | páginas: 16 | com texto: 16
Chunks indexados: 16

Gerando Tutorial...
OK | chamar_gemini

Gerando Flashcards...
OK | chamar_groq

Gerando Quiz...
OK | chamar_gemini

Gerando TL;DR...
OK | chamar_groq

Gerando Roteiro...
OK | chamar_groq

Gerando Resumo...
OK | chamar_groq

Finalizado. 6/6 formatos gerados.
```

O provedor utilizado pode variar conforme a disponibilidade das APIs.

### 7.4. Arquivos gerados

Os resultados são salvos automaticamente em:

```text
rag/resultados_teste_local/
```

Arquivos:

```text
tutorial.json
flashcards.json
quiz.json
tldr.json
roteiro.json
resumo.json
```

Esses arquivos são resultados locais e não precisam ser enviados ao GitHub.

A pasta `resultados_teste_local/` deve estar incluída no `.gitignore`.

---

## 8. Visualização dos resultados

Para visualizar os conteúdos gerados sem consumir novas chamadas de API, utilize:

```text
rag/visualizar_resultados_teste.ipynb
```

### Procedimento

1. Abra o notebook no VS Code.
2. Selecione o kernel Python com as dependências instaladas.
3. Execute as células.
4. Examine os seis produtos gerados.

O notebook lê os arquivos JSON existentes.

Caso o diretório de trabalho seja diferente, ajuste o caminho para `resultados_teste_local/`.

Uma alternativa é abrir os arquivos JSON diretamente no VS Code.

**Importante:** visualizar resultados existentes não executa novamente o pipeline e não consome tokens de Gemini ou Groq.

---

## 9. Gemini e fallback Groq

O Gemini é o provedor principal de geração de conteúdo.

Se ocorrer uma falha durante a geração, o pipeline pode tentar o Groq como provedor alternativo.

Exemplos de falhas que podem provocar o fallback incluem indisponibilidade do serviço e limites de utilização.

### Erro 429 — RESOURCE_EXHAUSTED

O erro `429` indica que algum limite ou cota da API foi atingido.

Isso pode envolver:

- Limite de requisições por minuto.
- Limite de tokens por minuto.
- Limite de utilização diária.
- Outras restrições do projeto ou modelo.

Um erro `429` não significa necessariamente que a utilização está bloqueada pelo restante do dia.

A disponibilidade do fallback depende também das cotas e das condições de uso do Groq.

### Registro de geração

O pipeline disponibiliza informações como:

- Provedor utilizado.
- Duração da geração.
- Erros ocorridos em tentativas anteriores.
- Produto final validado.

Essas informações são úteis para diagnóstico, monitoramento e análise do desempenho técnico do pipeline.

---

## 10. Resultado do teste realizado

Em **02/11/2026**, o teste de integração foi executado utilizando `Machine_Learning.pdf`.

| Indicador | Resultado |
|---|---|
| Páginas extraídas | 16 |
| Páginas com texto | 16 |
| Chunks indexados | 16 |
| Produtos solicitados | 6 |
| Produtos gerados | 6 |
| Gerações com Gemini | 2 |
| Gerações com Groq | 4 |

Os seis produtos foram gerados e salvos em JSON.

O teste confirmou o funcionamento conjunto da extração, indexação, recuperação, geração e validação no ambiente utilizado.

**Limitação:** esse resultado não garante funcionamento automático em outros computadores, nem comprova a qualidade pedagógica de todos os conteúdos gerados.

---

## 11. Benchmark RAG

O benchmark foi desenvolvido para avaliar configurações de segmentação, recuperação e reranking de documentos.

### 11.1. Provedores utilizados

O benchmark utiliza Voyage AI:

- Embeddings: `voyage-4`
- Reranking: `rerank-3`

O pipeline principal utiliza Gemini.

**As métricas obtidas com Voyage AI não validam automaticamente o desempenho do pipeline com Gemini.**

As configurações selecionadas a partir do benchmark devem ser consideradas hipóteses de trabalho para a implementação atual.

### 11.2. Documentos avaliados

Foram considerados cinco documentos:

- `Machine_Learning.pdf`
- `Deep_learning.pdf`
- `LLM.pdf`
- `redes_neurais.pdf`
- `vcn-deployment-guide.pdf`

Os PDFs originais do benchmark não foram incluídos na entrega por precaução quanto aos direitos de redistribuição.

### 11.3. Configurações avaliadas

O experimento considerou combinações de:

| Parâmetro | Valores |
|---|---|
| Chunk size | 500, 1.000, 1.500 e 2.000 |
| Overlap | 10% e 20% |
| K Retriever | 5, 10 e 15 |
| Top N Reranker | 3 e 5, quando compatível com K |

Foram avaliadas 40 configurações por documento, totalizando 200 combinações documento-configuração.

### 11.4. Script principal

```text
rag/benchmark/analisar_benchmark_rag_automatico_otimizado2_corrigido.py
```

O script utiliza os endpoints REST da Voyage AI.

Não é necessário instalar o SDK `voyageai` se as chamadas forem realizadas diretamente com `requests`.

### 11.5. Executar o benchmark

Coloque os PDFs necessários na pasta indicada pela documentação de `benchmark/pdfs/` e configure `VOYAGE_API_KEY` conforme a leitura de variáveis do script.

No PowerShell:

```powershell
cd .\rag\benchmark
python .\analisar_benchmark_rag_automatico_otimizado2_corrigido.py
```

**Atenção:** executar novamente o benchmark consome chamadas à API Voyage AI e pode atualizar os resultados existentes.

Não é necessário repetir o benchmark para utilizar os resultados já produzidos.

### 11.6. Resultados

Os resultados do benchmark estão organizados em arquivos CSV, incluindo:

- Métricas gerais por configuração.
- Resultados detalhados das consultas.
- Auditoria de chunks recuperados.

Os resultados devem ser consultados na pasta de análise do benchmark.

### 11.7. Notebook de análise

```text
rag/benchmark/analisar_benchmark_top10_5_pdfs.ipynb
```

Esse notebook permite comparar configurações e consultar rankings utilizando os CSVs existentes.

A análise dos resultados salvos não requer novas chamadas às APIs.

---

## 12. Extração provisória de documentos

O diretório `extrator_temporario/` contém uma implementação baseada em `pypdf`, utilizada durante o desenvolvimento e os testes de integração.

Sua finalidade é permitir que o pipeline seja testado independentemente da implementação definitiva de extração de documentos.

Essa implementação:

- Extrai texto de PDFs com camada textual.
- Organiza o conteúdo para utilização pelo pipeline.
- Não realiza OCR.
- Não substitui o extrator definitivo desenvolvido pela equipe.

Quando o componente definitivo estiver disponível, a equipe poderá substituir o extrator provisório, preservando os contratos de dados necessários à integração.

---

## 13. Segurança e arquivos locais

Não devem ser enviados ao GitHub:

- Arquivos `.env` com credenciais reais.
- Ambientes virtuais.
- Bancos de dados locais.
- Resultados temporários de testes.
- Arquivos de cache.
- PDFs sem autorização de redistribuição.

O arquivo `rag/.gitignore` deve contemplar, entre outros:

```gitignore
.env
.env.*
!.env.example

.venv/
venv/
__pycache__/
*.py[cod]
.ipynb_checkpoints/

*.db
*.sqlite
*.sqlite3

/resultados_teste_local/

benchmark/pdfs/**/*.pdf
benchmark/chroma*/

*.log
*.zip
```

O arquivo `.env.example` deve conter somente nomes de variáveis e valores fictícios.

---

## 14. Limitações conhecidas

1. O benchmark mede desempenho de recuperação e reranking, não a qualidade final das respostas educacionais.
2. O benchmark utiliza Voyage AI, enquanto o pipeline principal utiliza Gemini.
3. A extração de PDF é provisória e não possui OCR.
4. O funcionamento das APIs depende de credenciais, disponibilidade e cotas dos provedores.
5. O teste de integração foi validado localmente, mas ainda não foi reproduzido em uma instalação limpa.
6. A entrega não inclui a interface definitiva do NovaMente nem o banco de dados de produção.
7. Os imports poderão precisar de ajustes durante a integração com os demais componentes da equipe.
8. As versões das dependências foram definidas para o módulo, mas sua compatibilidade completa em outros ambientes ainda precisa ser verificada.

---

## 15. Recomendações para integração pela equipe

Para incorporar os componentes à aplicação definitiva:

1. Utilizar os contratos Pydantic como referência para a comunicação entre módulos.
2. Integrar o extrator definitivo ao formato de entrada esperado pelo pipeline.
3. Centralizar a configuração de credenciais e modelos.
4. Preservar o mecanismo de fallback entre provedores.
5. Validar os produtos gerados antes de armazená-los ou apresentá-los ao usuário.
6. Integrar os resultados à persistência e à interface desenvolvidas pelos demais integrantes.
7. Reexecutar o teste de integração após mudanças relevantes nos módulos.

O arquivo `teste_integracao.py` deve permanecer como uma forma simples de verificar se os componentes continuam funcionando em conjunto.

---

## 16. Execução rápida

Para integrantes que desejam apenas testar a geração dos seis produtos, execute os comandos abaixo a partir da raiz do repositório, no PowerShell:

```powershell
# 1. Criar ambiente virtual
python -m venv .venv

# 2. Ativar ambiente
.\.venv\Scripts\Activate.ps1

# 3. Instalar dependências
python -m pip install -r .\rag\requirements.txt

# 4. Criar configuração local
Copy-Item .\rag\.env.example .\rag\.env

# 5. Editar rag/.env e inserir as chaves de API

# 6. Executar teste
python .\rag\teste_integracao.py .\rag\Machine_Learning.pdf
```

Após a execução, consulte:

```text
rag/resultados_teste_local/
```

Ou abra:

```text
rag/visualizar_resultados_teste.ipynb
```

**Resultado esperado:** geração de Tutorial, Flashcards, Quiz, TL;DR, Roteiro e Resumo, com validação Pydantic e arquivos JSON disponíveis para inspeção.

---

**Status da entrega:** pipeline integrado e testado localmente com sucesso; disponível para integração com os demais componentes do NovaMente.