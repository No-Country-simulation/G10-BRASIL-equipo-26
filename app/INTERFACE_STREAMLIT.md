# 💻 Módulo da Interface (Frontend - Streamlit) · MentorIA-Tech

Este diretório contém a interface interativa do **MentorIA-Tech**, construída com [Streamlit](https://streamlit.io/) e desenhada sob a identidade visual oficial do **Brandbook UX/UI v1.1** para atender a todos os requisitos do **Hackathon ONE G10 (Alura & Oracle)**.

---

## 🎨 Identidade Visual e Experiência Digital (Brandbook UX/UI)

A interface foi projetada sob o conceito: *"Aprender com clareza, leveza e autonomia"*, aplicando rigorosamente as diretrizes da marca:

1. **Tokens de Cores Padronizados:**
   - **Verde Menta (`#A8E6CF`):** Cor primária para ações principais, destaques e confirmações.
   - **Lilás Pastel (`#CDB4DB`) / Lavanda (`#EDE4F5`):** Cor secundária para botões secundários e apoios.
   - **Rosa Suave (`#FFC8DD`) / Rosa Pálido (`#FFF0F5`):** Cor de destaque visual e cards de contextualização.
   - **Grafite (`#293241`):** Tipografia com alto contraste e conformidade estrita com **WCAG AA** (texto escuro sobre fundos claros).
   - **Bordas Arredondadas:** `16px` para cards e `10px` para controles de formulário.

2. **Assets e Identidade Integrados (`app/assets/`):**
   - **Ícone Principal:** Usado no Favicon da aba do navegador (`page_icon`) com recorte automático de transparência.
   - **Logomarca Principal:** Posicionada no topo da Sidebar com fundo claro, preservando contraste e legibilidade.
   - **Mascote Oficial:** Integrado no Banner Principal (*Hero*) da Visão Geral e nos estados vazios (*Empty States*) para humanizar a experiência do estudante.

---

## 📌 Telas e Funcionalidades Implementadas

O aplicativo organiza a jornada do usuário em 4 etapas didáticas:

### 1. ◫ Visão Geral
- **Hero Banner:** Apresentação da proposta de valor com o Mascote oficial do MentorIA-Tech.
- **Painel de Métricas:** Contadores de documentos indexados, conteúdos adaptados gerados, formatos explorados e status do bucket **OCI Object Storage Always Free**.
- **Demonstrações Recentes do MVP:** Lista rápida dos últimos materiais adaptados com botão direto para inspeção.
- **Jornada de Criação:** Resumo das 4 etapas de aprendizado.

### 2. ▤ Minha Biblioteca (Ingestão Real de Documentos)
- **Upload Multiformato:** Suporte nativo para envio de arquivos `.pdf`, `.md` e `.txt`.
- **Extração com Mapeamento de Páginas:** Extração automatizada de texto página por página (via `pypdf`) para indexação precisa e citação de fontes no RAG.
- **Entrada Manual de Texto:** Permite colar textos técnicos diretamente na interface.
- **Acervo de Fontes:** Visualização de metadados dos materiais (quantidade de páginas, caracteres, tipo de arquivo e prévia do conteúdo).
- **Fontes Base Incluídas:**
  - *Introdução à Arquitetura de Redes VCN na OCI* (Redes Virtuais, Sub-redes, Security Lists e Gateways).
  - *Fundamentos de Machine Learning e Modelos Preditivos* (Conceitos, datasets, tipos de aprendizagem e cross-validation).

### 3. ✧ Estúdio de Criação (Geração com IA + RAG)
- **Parametrização Flexível:**
  - **Material de Origem:** Seleção a partir da biblioteca de documentos.
  - **Perfil do Destinatário:** *Iniciante / Transição*, *Desenvolvedor Jr/Pleno*, *Líder Técnico / Arquiteto* e *Gestor / Executivo*.
  - **Nível de Profundidade:** *Básico*, *Intermediário* e *Avançado*.
  - **Quantidade de Itens:** Slider customizável de 3 a 8 itens.
  - **Instruções Adicionais:** Campo opcional de estilo (ex: analogias do dia a dia, comandos práticos).
  - *(Conforme alinhamento na reunião de 09/11/2026, o campo Nicho foi simplificado para foco exclusivo em Tecnologia).*
- **6 Formatos Pedagógicos Suportados:**
  1. **Flashcards de Memorização:** Cartões com pergunta, resposta, dica didática e classificação.
  2. **Quiz Interativo:** Questões com alternativas e verificação em tempo real de acerto/erro com explicação didática imediata.
  3. **Guia Passo a Passo (Tutorial):** Etapas numeradas com orientações práticas e dicas.
  4. **Resumo Executivo (TL;DR):** Síntese condensada com pontos-chave destacados.
  5. **Roteiro de Aula / Vídeo:** Sequência cronológica com minutagem estimada por atividade.
  6. **Resumo Estruturado:** Seções temáticas aprofundadas.
- **Rastreabilidade e Ancoragem:** Cada item gerado exibe badges indicando a página e o chunk exato de onde a informação foi extraída na documentação original.
- **Sistema de Avaliação do Usuário (Feedback):** Módulo de feedback por estrelas (1 a 5) e campo de comentário para alimentar métricas de BI e validação da proposta de valor do MVP.

### 4. ▣ Meus Conteúdos (Histórico, Contratos & OCI)
- **Abas de Inspeção:**
  - **📖 Estudo Interativo:** Navegação completa por todos os itens pedagógicos gerados.
  - **🧾 Inspeção JSON (Contratos):** Comparação lado a lado do payload de entrada e do schema oficial `PacoteFinal` do Pydantic.
  - **☁️ Persistência OCI & Exportações:** Detalhes da sincronização no bucket Always Free da Oracle Cloud Infrastructure e downloads multiformato.

---

## 📦 Exportação Multiformato (Requisito do Edital)

Para cada conteúdo gerado, o MentorIA-Tech oferece 3 opções diretas de exportação:
1. **⬇️ Baixar JSON (Schema Oficial):** Arquivo JSON estruturado em conformidade com o schema `PacoteFinal` e `output_schema.json`.
2. **📝 Baixar Markdown:** Arquivo formatado em Markdown com títulos, alertas e dicas, pronto para Notion, Obsidian ou GitHub.
3. **🗂️ Baixar CSV (Compatível com Anki):** Arquivo formatado com delimitador `;` para importação direta de baralhos no software de repetição espaçada **Anki**.

---

## 🛠️ Como rodar a aplicação localmente

### 1. Criar e ativar o ambiente virtual
```powershell
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Instalar as dependências
```powershell
pip install -r app/requirements.txt
```

### 3. Iniciar o MentorIA-Tech
```powershell
streamlit run app/main.py
```
Acesse no seu navegador: `http://localhost:8501`.
