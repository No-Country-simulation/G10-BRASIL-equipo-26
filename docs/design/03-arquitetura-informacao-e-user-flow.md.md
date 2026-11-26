# Arquitetura de Informação e Fluxo de Navegação — MentorIA Tech

* **Etapa de Design:** Arquitetura de Informação (AI) & Fluxo de Usuário (*User Flow*)
* **Objetivo:** Estruturar a navegação principal da plataforma, definir a hierarquia de informações de cada tela e mapear o fluxo de ponta a ponta entre ingestão de fontes, estúdio de geração e consumo de conteúdo.

---

## 1. Mapa do Site (Sitemap & Navegação Principal)

A plataforma organiza-se em **4 módulos centrais** acessíveis via barra lateral (desktop) ou barra inferior/menu gaveta (mobile), separando claramente o **ciclo de produção** do **ciclo de estudo**:

```text
MentorIA Tech
├── 1. Home (Dashboard & Visão Geral)
│   ├── Resumo de conteúdos educacionais criados (Progresso & Retomada rápida)
│   ├── Atalhos de Ação Rápida (Subir Fonte / Abrir Estúdio)
│   └── Indicadores de Estudo (Quizzes concluídos, Flashcards revisados, Fontes ativas)
│
├── 2. Biblioteca de Fontes (Gestão de Insumos Técnicos)
│   ├── Upload de Novos Documentos (PDF, MD, TXT)
│   ├── Catálogo de Fontes Indexadas (Busca, Filtros por Tag/Stack, Status RAG)
│   └── Detalhes da Fonte (Metadados, Trechos extraídos, Ação: "Enviar para Estúdio")
│
├── 3. Estúdio de Criação (Motor de Parametrização & Pré-visualização)
│   ├── Passo 1: Seleção da(s) Fonte(s) da Biblioteca
│   ├── Passo 2: Parametrização do Estudo (Tipo de artefato, Quantidade de itens/questões, Perfil, Nível técnico)
│   ├── Passo 3: Acionamento da IA (Pipeline RAG com feedback de progresso)
│   └── Passo 4: Área de Pré-visualização (Revisão, Ajustes/Regeneração e Exportação)
│
└── 4. Biblioteca de Conteúdo (Repositório de Artefatos Prontos)
    ├── Organização por Capacitação / Pasta / Stack Tecnológica
    ├── Visualizador Interativo por Formato:
    │   ├── Resumo Executivo (Leitura estruturada com citações da fonte)
    │   ├── Passo a Passo Prático (Checklist acionável + blocos de código copiáveis)
    │   ├── Deck de Flashcards (Modo virar carta + marcação "Dominei / Revisar")
    │   └── Quiz Interativo (Questões com feedback imediato e justificativa)
    └── Opções de Exportação Externa (Markdown `.md` / CSV para Anki / JSON)
```

---

## 2. Especificação Funcional e Diretrizes de UI por Módulo

### 2.1. Home (Dashboard Geral)
* **Propósito:** Reduzir o tempo até a retomada do estudo (*Time-to-Action*) e dar visibilidade imediata sobre o que já foi criado.
* **Componentes-Chave:**
  * **Primeiros passos:** Orienta o usuário de forma objetiva a explorar a plataforma.
  * **Cards de Conteúdos Gerados:** Exibem título do documento, barra de progresso (ex.: *Passo a passo 60% concluído • Quiz pendente*) e botão *"Continuar Estudando"*.
  * **Seção "Continuar de onde parou":** Acesso direto ao último artefato aberto na Biblioteca de Conteúdo ou rascunho pendente no Estúdio de Criação.
  * **Métricas Simples de Consistência:** Contadores objetivos (documentos estudados, taxa média de acerto nos quizzes) sem gamificação excessiva.

### 2.2. Biblioteca de Fontes (Catálogo de Documentações)
* **Propósito:** Centralizar as documentações técnicas indexadas pelo RAG para que o usuário possa reutilizá-las múltiplas vezes sem novos uploads.
* **Componentes-Chave:**
  * **Área de Upload (Drag & Drop):** Suporte inicial a `PDF`, `MD` e `TXT` com validação clara de tamanho e formato.
  * **Cards/Lista de Fontes:** Exibem título do documento, formato, data de envio, tags tecnológicas (ex.: `OCI`, `Java`, `Docker`) e badge de status (`Indexado • Pronto para uso` ou `Processando`).
  * **Ação Primária:** Botão *"Gerar Conteúdo no Estúdio"* diretamente no card da fonte.

### 2.3. Estúdio de Criação (Parametrização + Pré-visualização)
* **Propósito:** Dar controle pedagógico ao estudante antes de consolidar o material, eliminando a caixa-preta das IAs genéricas.
* **Layout Recomendado (Split-View no Desktop / Etapas Guiadas no Mobile):**
  * **Painel Esquerdo — Configuração & Parâmetros:**
    * *Fonte(s) Selecionada(s):* Escolha de 1 ou mais documentos da Biblioteca de Fontes.
    * *Artefatos a Gerar (Checkboxes):* Resumo Estruturado, Passo a Passo Prático, Flashcards, Quiz Interativo.
    * *Parâmetros Pedagógicos:* Nível de profundidade (*Introdutório / Intermediário / Avançado*), Quantidade de questões/cards (ex.: 5, 10, 15) e Foco opcional (ex.: *"Focar em configuração e tratamento de erros"*).
    * *CTA Principal:* Botão **"Gerar Conteúdo com IA"**.
  * **Painel Direito — Área de Pré-visualização (*Live Preview*):**
    * Exibe o conteúdo gerado em abas antes de salvar definitivamente.
    * Permite ao usuário **validar o formato e conteúdo gerado**, descartar ou **regenerar** um item.
    * *CTA de Consolidação:* Botão **"Salvar na Biblioteca de Conteúdo"** (com opção de vincular a uma pasta).

### 2.4. Biblioteca de Conteúdo (Repositório de Estudo Ativo)
* **Propósito:** Ambiente livre de distrações otimizado para leitura técnica, execução prática ao lado da IDE e revisão rápida em dispositivos móveis.
* **Componentes-Chave:**
  * **Filtros e Busca:** Filtragem por tipo de artefato (*Todos*, *Resumos*, *Passo a Passo*, *Flashcards*, *Quizzes*) e por tags de tecnologia.
  * **Requisitos Críticos de UI para Conteúdo Técnico:**
    * *Syntax Highlighting* (coloração de sintaxe) em todos os blocos de código.
    * Botão *"Copiar código"* em 1 clique nos guias de Passo a Passo.
    * Rastreabilidade: badge discreto indicando o trecho/página da fonte original que fundamentou a resposta do Quiz ou Resumo.

---

## 3. Fluxo Completo do Usuário (User Flow Ponta a Ponta)

```text
[1. HOME]
   │
   ├──► (Usuário já tem fonte) ───────────────────────┐
   │                                                  ▼
   └──► (Nova documentação) ──► [2. BIBLIOTECA DE FONTES]
                                      │
                                      ▼ (Upload + Indexação RAG concluída)
                                [3. ESTÚDIO DE CRIAÇÃO]
                                      │
                                      ├──► Seleciona Fonte + Parâmetros
                                      ├──► Aciona IA (Geração via RAG)
                                      ├──► Pré-visualiza Artefatos
                                      │      ├── (Precisa ajuste?) ──► Regenera seção
                                      │      └── (Aprovado!) ─────────┐
                                      ▼                                │
                                [Exporta / Salva] ◄────────────────────┘
                                      │
                                      ▼
                            [4. BIBLIOTECA DE CONTEÚDO]
                                      │
                                      ├──► Lê Resumo / Executa Passo a Passo
                                      ├──► Pratica Flashcards & Responde Quiz
                                      └──► Atualiza progresso refletido na [1. HOME]
```

---

## 4. Checklist de Transição para UI Design (Próxima Etapa)
- [ ] **Wireframes de Baixa Fidelidade:** Esboçar as 4 telas principais priorizando o *Split-View* do **Estúdio de Criação** e a experiência de leitura na **Biblioteca de Conteúdo**.
- [ ] **Design System Básico (Tokens):** Definir paleta de cores (incluindo suporte a *Dark Mode*, altamente preferido por desenvolvedores), tipografia monoespaçada para blocos de código e componentes de feedback de IA.
- [ ] **Protótipo Navegável & Teste com Usuários ONE:** Validar se a separação entre *Biblioteca de Fontes* e *Biblioteca de Conteúdo* é intuitiva sem necessidade de tutorial.