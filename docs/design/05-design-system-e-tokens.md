# Design System & Tokens de Interface — MentorIA Tech

* **Etapa de Design:** UI Design & Especificação de Handoff
* **Base Conceitual:** *Brandbook MentorIA Tech (Versão 1.1)* — "Aprender com clareza, leveza e autonomia."
* **Objetivo:** Padronizar cores, tipografia, espaçamentos, regras de acessibilidade e componentes reutilizáveis para garantir consistência entre o protótipo e a aplicação final.

---

## 1. Essência Visual e Personalidade

O sistema visual equilibra a **suavidade acolhedora dos tons pastéis** (reduzindo a ansiedade e a fadiga visual diante de documentações técnicas densas) com o **rigor técnico de blocos de código em alto contraste**.

* **Pilares:** Clara • Acolhedora • Criativa
* **Tom de Voz (UX Writing):** Simples sem infantilizar; didático sem excesso de jargão; encorajador sem exageros; objetivo nas mensagens de erro e estados vazios.

---

## 2. Tokens de Cor (Design Tokens)

### 2.1. Paleta Cromática da Marca e Superfícies

| Token CSS | Valor Hex | Papel Semântico | Uso Recomendado |
| :--- | :--- | :--- | :--- |
| `--color-primary` | `#A8E6CF` | Verde Menta (Principal) | Ações positivas, indicadores de progresso, elementos de cognição/aprendizado. |
| `--color-secondary` | `#CDB4DB` | Lilás Pastel (Secundária) | Elementos de IA/RAG, seleções ativas de menu, badges de formato. |
| `--color-accent` | `#FFC8DD` | Rosa Suave (Destaque) | Destaques pontuais, avatar, tags de atenção leve. |
| `--color-action-primary` | `#8065D5` | Roxo Interativo (CTA) | Botões primários de ação (garante contraste WCAG AA com texto branco). |
| `--color-bg` | `#FAFAFC` | Off-White (Background) | Fundo geral da aplicação. |
| `--color-surface` | `#FFFFFF` | Branco Puro (Superfície) | Cards, sidebar, inputs e áreas de leitura principal. |
| `--color-surface-subtle` | `#F1F3F5` | Cinza Suave | Divisórias, bordas (`#EFEDF3`) e estados neutros. |
| `--color-text` | `#293241` | Grafite (Texto Principal) | Títulos, corpo de texto e rótulos sobre fundos claros/pastéis. |
| `--color-text-muted` | `#657080` | Cinza Médio (Apoio) | Subtítulos, metadados, placeholders e breadcrumbs. |

### 2.2. Suporte Técnico: Blocos de Código e Dark Mode

Para atender à persona de desenvolvedores (programa ONE) e preservar a legibilidade de sintaxe em tutoriais, flashcards e quizzes:
* **Superfície de Código (`--color-code-bg`):** `#29283B` (Grafite Profundo)
* **Texto de Código (`--color-code-fg`):** `#EEE9FF` (Lavanda Clara de Alto Contraste)
* **Diretriz de Evolução (Dark Mode):** Os tokens semânticos (`--color-bg`, `--color-surface`, `--color-text`) foram estruturados para permitir a inversão futura para tema escuro mantendo os acentos em `#A8E6CF` (Menta) e `#CDB4DB` (Lilás) sem perda de contraste.

---

## 3. Tipografia e Escala Hierárquica

* **Família Principal (UI & Leitura):** `Inter`, `system-ui`, `-apple-system`, `Segoe UI`, `sans-serif`
* **Família Técnica (Código & Comandos):** `ui-monospace`, `SFMono-Regular`, `JetBrains Mono`, `monospace`

| Estilo | Tamanho | Peso | Line-Height | Aplicação |
| :--- | :--- | :--- | :--- | :--- |
| **Eyebrow / Kicker** | `12px` | `800` (ExtraBold) | `1.2` | Rótulos superiores em caixa alta (`letter-spacing: 1.2px`). |
| **Título de Página (`H1`)** | `28px – 32px` | `600 – 800` | `1.2` | Cabeçalho principal de cada módulo. |
| **Subtítulo (`H2`)** | `18px – 22px` | `600 – 700` | `1.3` | Títulos de cards e seções internas. |
| **Corpo de Texto** | `14px – 16px` | `400` (Regular) | `1.6` | Parágrafos explicativos, respostas de flashcards e resumos. |
| **Bloco de Código** | `12px – 13px` | `400` (Mono) | `1.65` | Trechos de código, comandos CLI e payloads JSON. |

---

## 4. Geometria, Espaçamento e Componentes

### Tokens Estruturais
* `--radius-hero`: `24px` (Banner de destaque da Home)
* `--radius-card`: `16px – 19px` (Cards de conteúdo, métricas e painéis do Estúdio)
* `--radius-control`: `10px – 12px` (Botões, inputs, selects e itens de navegação)
* `--radius-pill`: `30px` (Badges de status e tags de formato)

### Padrões de Componentes (MVP)
1. **Botões:**
   * *Primário (`#8065D5` + texto `#FFFFFF`):* Ações principais (`Criar conteúdo`, `Adicionar texto`).
   * *Secundário Menta (`#A8E6CF` + texto `#245D47`):* Ações de estímulo ao estudo (`Adicionar uma fonte`).
   * *Terciário / Light (`#FFFFFF` + borda `#E7E1F0` + texto `#6C58A7`):* Ações de suporte (`Ver todos`, `Abrir`, `Excluir`).
2. **Cards de Formato Pedagógico (Estúdio):** Grid selecionável com borda de `2px solid #9A81E6` e fundo `#F5F1FF` no estado ativo (`selected`).
3. **Feedback de Sistema (Toasts & Callouts):**
   * *Toast Flutuante:* Canto inferior direito (`#332C4E` com texto branco) para confirmações rápidas.
   * *Banner Informativo:* Fundo suave (`#FFF9E8` com texto `#8C7850`) para avisos de escopo/RAG.

---

## 5. Regras de Acessibilidade e Governança (WCAG)

* **Contraste Obrigatório:** **Nunca** utilizar texto branco (`#FFFFFF`) diretamente sobre fundos pastéis (`#A8E6CF`, `#CDB4DB`, `#FFC8DD`). Utilizar sempre grafite escuro (`#293241` ou `#245D47`) para garantir legibilidade nível **WCAG AA**.
* **Redundância Visual de Estados:** Nunca depender exclusivamente de cor para comunicar erro, sucesso ou seleção; combinar sempre com **ícone + rótulo textual** (ex.: badge `PDF: extração pendente` vs. `Texto disponível`).
* **Responsividade:** Breakpoints definidos em `1100px` (colapso de grids de 4 para 2 colunas e empilhamento do Split-View) e `700px` (transformação da sidebar em menu gaveta *off-canvas*).