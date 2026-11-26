# Wireframes de Baixa Fidelidade & Prompts (Google Stitch) — MentorIA Tech

* **Etapa de Design:** Ideação de Interface & Estruturação de Layout (UI Wireframing)
* **Objetivo:** Documentar a estrutura visual de baixa/média fidelidade das 4 telas principais da plataforma e fornecer prompts otimizados para geração de wireframes no **Google Stitch**.

---

## 1. Diretrizes Estruturais dos Wireframes

O layout da aplicação segue um **Shell Persistente** composto por:
* **Barra Lateral Esquerda (Sidebar Fixa - 246px):** Logotipo *MentorIA Tech*, menu de navegação principal com os 4 pilares e card de propósito no rodapé.
* **Barra Superior (Topbar - 78px):** Breadcrumb dinâmico de localização, badge de status do ambiente e avatar do usuário.
* **Área de Conteúdo Fluida (Max-width 1450px):** Grid responsivo com cards arredondados (`16px`–`19px`), espaçamento generoso e hierarquia visual clara.

### Ajuste de Escopo Aplicado (Nicho EdTech)
* No **Estúdio de Criação**, o campo *"Contexto de aplicação / Setor"* foi removido para eliminar atrito cognitivo, mantendo o foco 100% direcionado ao aprendizado técnico e capacitação no ecossistema de tecnologia (programa ONE).

---

## 2. Prompts para o Google Stitch

Abaixo estão os prompts estruturados usados para geração dos wireframes no **Google Stitch**, tela por tela, em modo **Desktop Web App (1440x900)** utilizando estilo *Clean Low-Fidelity Wireframe / Minimal SaaS UI*.

### Prompt 1 — Tela: Home (Visão Geral / Dashboard)
> **Copiar e colar no Google Stitch:**
> ```text
> Design a clean, modern EdTech web application dashboard wireframe in Portuguese called "MentorIA Tech". 
> Layout structure:
> - Left fixed sidebar (240px) with brand logo "MentorIA Tech" at top, navigation menu with 4 items ("Visão geral" active, "Minha biblioteca", "Estúdio de criação", "Meus conteúdos"), and a small motivational card at the bottom.
> - Top header bar with breadcrumb "Espaço de aprendizagem / Visão geral", a status pill badge, and user avatar circle.
> - Main content area:
>   1. Hero banner card with eyebrow label "SEU ESPAÇO DE APRENDIZAGEM", headline "Ideias complexas, aprendizado mais leve.", short subtitle, primary CTA button "Criar conteúdo educativo", and a minimalist book/sparkle illustration placeholder on the right.
>   2. A 4-column KPI stats grid showing cards for: "Fontes adicionadas", "Conteúdos criados", "Formatos explorados", and "Progresso de estudo".
>   3. Bottom 2-column asymmetric split section: Left wider card titled "Seus conteúdos recentes" with a list of study items (icon, title, format tag, date, and "Abrir" button) and "Ver todos" link; Right narrower card titled "Seu próximo passo" showing a 3-step onboarding checklist (1. Adicione seu material, 2. Personalize o público e formato, 3. Explore e exporte o resultado) and a CTA button "Adicionar uma fonte".
> Style: Clean SaaS wireframe, rounded cards (16px radius), generous whitespace, clear visual hierarchy, no clutter.
> ```

### Prompt 2 — Tela: Biblioteca de Fontes (Minha Biblioteca)
> **Copiar e colar no Google Stitch:**
> ```text
> Design a clean EdTech web application wireframe in Portuguese for "Minha biblioteca" (Source Library) inside "MentorIA Tech".
> Layout structure:
> - Keep the persistent left sidebar ("Minha biblioteca" active) and top header with breadcrumb "Espaço de aprendizagem / Minha biblioteca".
> - Main content area header: Eyebrow "ORGANIZE SEU CONHECIMENTO", title "Minha biblioteca", subtitle "Reúna os materiais técnicos que servirão de base para a adaptação educativa."
> - Two-column asymmetric split layout (1.35fr / 1fr):
>   - Left column card titled "Adicionar material": Contains a large dashed drag-and-drop file upload box with cloud icon ("Clique para selecionar arquivos - PDF, Markdown ou TXT"), helper note about text extraction, followed by a divider, a text input labeled "Título do material", a multi-line textarea labeled "Ou cole um texto técnico", and a full-width primary button "+ Adicionar texto à biblioteca".
>   - Right column card titled "Materiais disponíveis" with a counter badge ("3 fontes"): A vertical list of uploaded technical documents, each row showing a document icon, file title, file type and status subtitle (e.g., "PDF · Indexado via RAG"), a primary quick-action button "Estudar" and a secondary "Excluir" button.
> Style: Clean low-fidelity SaaS wireframe, rounded containers, clear form labels, accessible button spacing.
> ```

### Prompt 3 — Tela: Estúdio de Criação (Split-View de Parametrização e Pré-visualização)
> **Copiar e colar no Google Stitch:**
> ```text
> Design a split-view EdTech AI Creation Studio wireframe in Portuguese called "Estúdio de criação" inside "MentorIA Tech".
> Layout structure:
> - Persistent left sidebar ("Estúdio de criação" active) and top header with breadcrumb "Espaço de aprendizagem / Estúdio de criação".
> - Page header: Eyebrow "SEU ESTÚDIO CRIATIVO", title "Crie uma nova experiência", subtitle "Configure como seu conteúdo será apresentado a partir da sua documentação técnica."
> - Two-column workspace split-view (45% left configuration panel / 55% right live preview panel):
>   - Left Panel Card ("01 · Personalização"):
>     - Dropdown select labeled "Material de origem" (e.g., "spring-security-jwt.pdf").
>     - Two side-by-side dropdown selects: "Perfil do destinatário" (e.g., "Iniciante / Transição de carreira") and "Nível de detalhe" (e.g., "Didático", "Objetivo", "Aprofundado"). Do NOT include sector or industry fields.
>     - Section "02 · Formato pedagógico": A 3-column grid of selectable icon cards for "Flashcards (Memorização)", "Quiz (Pratique)", "Tutorial (Passo a passo)", "Resumo executivo (TL;DR)", and "Roteiro de aula (Aula ou vídeo)".
>     - Info callout banner explaining RAG source grounding.
>     - Full-width primary CTA button "Criar conteúdo com IA".
>   - Right Panel Card ("03 · Prévia do conteúdo"):
>     - Card header with title, subtitle "Visualização interativa", and status badge "Pronto".
>     - Interactive preview body displaying a generated Flashcard / Tutorial snippet with a dark monospaced code block, source citation pill, and bottom action buttons "Salvar na Biblioteca" and "Exportar JSON".
> Style: Clean SaaS wireframe, high clarity, split-screen productivity layout.
> ```

### Prompt 4 — Tela: Biblioteca de Conteúdo (Meus Conteúdos)
> **Copiar e colar no Google Stitch:**
> ```text
> Design a clean EdTech Content Repository wireframe in Portuguese called "Meus conteúdos" inside "MentorIA Tech".
> Layout structure:
> - Persistent left sidebar ("Meus conteúdos" active) and top header with breadcrumb "Espaço de aprendizagem / Meus conteúdos".
> - Page header: Eyebrow "SEU ACERVO DE APRENDIZAGEM", title "Meus conteúdos", subtitle "Consulte os materiais de estudo gerados, pratique com quizzes e flashcards ou exporte os dados."
> - Filter bar above the main list: Search input field "Buscar por título ou tecnologia..." and pill filter tabs ("Todos", "Flashcards", "Quiz", "Tutorial", "Resumo").
> - Main Card ("Histórico de criação" with count pill):
>   - Clean list of generated study packages. Each row displays: format icon, study title (e.g., "Autenticação JWT com Spring Boot"), metadata subtitle ("Tutorial · Iniciante / Transição de carreira · Data"), and right-aligned action buttons ("Abrir estudo" primary light button, "JSON" export button).
> - Bottom subtle disclaimer banner regarding source-grounded RAG generation.
> Style: Clean low-fidelity SaaS wireframe, generous padding, scannable list rows, developer-friendly hierarchy.
> ```