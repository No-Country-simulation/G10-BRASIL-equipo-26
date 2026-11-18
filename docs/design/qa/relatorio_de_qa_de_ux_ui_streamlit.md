# 🎨 Relatório de Auditoria Design QA — Streamlit

> **Projeto:** MentorIA Tech (Desafio NovaMente) | Hackathon ONE — Grupo 10 (Equipe 26)
> **Referência Oficial:** [Guia de Design (`design.md`)](../design/design.md) | [Brandbook UX/UI](../design/MentorIA-Tech_Brandbook_UXUI.pdf)

Este documento registra a auditoria de **Design QA** da aplicação deployada no Streamlit, avaliando a fidelidade visual ao Brandbook, usabilidade da jornada, acessibilidade (WCAG AA), UX Writing, comportamento em Modo Claro/Escuro e impactos das limitações arquiteturais do Streamlit, com base na análise do código-fonte (`main.py` e `.streamlit/config.toml`) e nas capturas das 4 telas principais.

---

## 📋 Informações da Avaliação

| Campo | Detalhes |
| :--- | :--- |
| **URL da Aplicação (Streamlit)** | `https://mentoria-tech-ai.streamlit.app/` |
| **Data da Avaliação** | `18/11/2026` |
| **Avaliador(a) UX/UI** | `Lysara Pinheiro / @LysaJPDataLab` |
| **Escopo Analisado** | Código (`main.py`, `.streamlit/config.toml`) + Telas exportadas em **Modo Claro** e **Modo Escuro** (Visão geral, Minha biblioteca, Estúdio de criação, Meus conteúdos) |
| **Dispositivos / Viewports** | Desktop (paisagem via exportação) + Revisão de regras `@media (max-width: 768px)` no código *(teste interativo em mobile real pendente)* |
| **Status Geral de UX/UI** | 🔴 **Requer correções críticas no Modo Escuro e ajustes de UX/UI** *(Modo Claro com alta fidelidade ao Brandbook; Modo Escuro com falhas críticas de visibilidade e pontos de atrito inerentes ao Streamlit)* |

---

## 1. Resumo Executivo de UX/UI

*Síntese sobre a percepção geral da interface (clareza, leveza, autonomia e consistência visual):*

* **O que funciona muito bem (Modo Claro):**
  * **Fidelidade à paleta e tokens:** O `.streamlit/config.toml` e as variáveis CSS de `main.py` aplicam com precisão a paleta pastel (`#A8E6CF`, `#CDB4DB`, `#FFC8DD`), os fundos claros (`#FAFAFC` e `#FFFFFF`), a fonte `Inter` com fallback métrico e os raios de borda (`16px` em cards e `10px` em controles).
  * **Contraste em botões pastéis (WCAG AA/AAA):** O código resolve proativamente o problema clássico de botões pastéis no Streamlit, forçando texto escuro (`#1B3B2B` / `#293241`) sobre Verde Menta e Lavanda Clara, além de ajustar o texto secundário (`#4A5568`) para manter contraste $\ge 4.5:1$.
  * **Estados bem estruturados:** Estados vazios (*empty states*) presentes em todas as telas, feedback de carregamento passo a passo (`st.status`) com proteção contra duplo clique e tratamento de erros com detalhes técnicos recolhidos.

* **Principais pontos de atrito e limitações críticas:**
  * **Falhas graves de visibilidade no Modo Escuro:** Como o `config.toml` fixa `base = "light"`, o CSS customizado de Dark Mode entra em conflito com elementos nativos do Streamlit. Tags `<code>` mantêm fundo branco enquanto recebem texto claro (`#F8FAFC`), tornando nomes como o do bucket na sidebar **invisíveis**. Além disso, o **mascote** e alguns textos/elementos perdem contraste ou desaparecem sobre superfícies escuras.
  * **Limitações inerentes à arquitetura do Streamlit:** A aplicação sofre com **reruns totais de página (`st.rerun`)** a cada troca de aba, upload ou seleção de formato, gerando micro-paralisações perceptíveis para o estudante, além de **distribuição espacial rígida** no *Estúdio de criação*.
  * **Desequilíbrio visual e seleção monótona no Estúdio:** A coluna esquerda concentra todos os parâmetros e 6 opções em um `st.radio` linear e extenso, forçando rolagem até o botão de gerar, enquanto a coluna direita permanece com um grande espaço vazio antes da primeira geração.
  * **Sobrecarga de detalhes técnicos de infraestrutura:** Avisos como `Contrato v0.3: Envio via POST /geracoes (multipart/form-data) + persistência no bucket OCI`, `GET /quiz`, `SQLite`, `usuario_id` e a URL crua do Render dividem atenção com o fluxo educacional e destoam do tom de voz didático do Brandbook.
  * **Navegação por teclado (`:focus-visible`):** Ausência de estilo explícito de foco de alto contraste para botões, inputs e controles interativos.

---

## 2. Auditoria de Identidade Visual (Aderência ao Brandbook)

### Logotipo, Mascote e Marca
* [x] **Fundo prioritário (Logotipo):** Logotipo protegido sobre fundo claro na sidebar (`transparent` no modo claro sobre `#FFFFFF` e `#F8FAFC` no modo escuro).
* [x] **Área de respiro:** Container `.nm-brand-container` aplica `padding: 12px` e recorte controlado com `padding=12` no processamento da imagem, preservando margem limpa ao redor da marca.
* [ ] **Integridade visual no Modo Escuro (Mascote):** **Falha encontrada.** Diferente do logotipo, o mascote usa `--hero-mascote-bg: rgba(30, 41, 59, 0.90)` no Dark Mode e não recebe fundo claro no *empty state* do Estúdio, ficando invisível ou com contraste comprometido em telas escuras.

### Paleta de Cores e Superfícies
* [x] **Fundos e superfícies (Modo Claro):** Off-white (`#FAFAFC`) no fundo geral e Branco (`#FFFFFF`) nos cards (`stVerticalBlockBorderWrapper`) e sidebar.
* [x] **Cores de destaque:** Verde Menta (`#A8E6CF`) nas ações primárias e item ativo do menu; Lavanda/Lilás (`#EDE4F5` / `#CDB4DB`) nas ações secundárias e badges; Rosa Suave (`#FFC8DD` / `#FFF0F5`) no gradiente do hero e pills.
* [ ] **Consistência no Modo Escuro:** **Falha encontrada.** Elementos nativos (`<code>`, alertas e componentes baseados em `base = "light"`) não herdam corretamente os fundos escuros, gerando blocos brancos com texto branco ilegível.

### Tipografia e Espaçamento
* [x] **Família tipográfica:** `Inter` carregada via Google Fonts com `@font-face` de fallback métrico (`Inter Fallback`, `system-ui`), minimizando *layout shift* (CLS).
* [ ] **Escala e hierarquia:** `.nm-hero h1` (`1.85rem` / ~30px) e `.nm-section-title` (`1.28rem` / ~20px) seguem o Brandbook, mas `st.title()` nas páginas 2, 3 e 4 mantém o tamanho padrão do Streamlit (~44px), criando leve inconsistência de escala.
* [x] **Geometria e bordas:** Cards com `border-radius: 16px`, controles com `10px`, sombras suaves e bordas sutis (`#E5E7EB`).
* [ ] **Estrutura de tela e distribuição espacial:** A **sidebar** exige rolagem vertical devido ao bloco da API e rodapé, e o **Estúdio de criação** apresenta forte assimetria vertical (coluna esquerda muito longa exigindo rolagem até o CTA vs. coluna direita vazia).

---

## 3. Usabilidade, Jornada e UX Writing

### Clareza da Jornada (4 Etapas)

| Etapa | Critério de Experiência Avaliado | Status | Observações |
| :--- | :--- | :---: | :--- |
| **01. Fontes** | Área de upload/inserção de texto é intuitiva e indica claramente os formatos aceitos (PDF, MD, texto) | ✅ | Excelente oferta de 3 caminhos: upload, PDF de exemplo real (`Machine_Learning.pdf`) e texto manual. Recomenda-se apenas simplificar a menção a `multipart/form-data`. |
| **02. Personalizar** | Campos de perfil, nicho e formato são fáceis de preencher e possuem rótulos (*labels*) persistentes | ⚠️ | Rótulos persistentes OK, mas há 3 atritos: (1) *selectboxes* lado a lado truncam os textos (`Iniciante / ...`, `Básico (Did...`); (2) seleção dos 6 formatos via `st.radio` clássico é linear e monótona; (3) formulário longo empurra o CTA para fora da primeira dobra. |
| **03. Gerar** | Ação principal é evidente e o tempo de espera oferece feedback visual claro de progresso | ⚠️ | Bom `st.status` e proteção contra duplo clique. Porém, o aviso técnico *"Contrato v0.3"* compete com o botão principal, falta atalho direto para *Minha biblioteca* quando não há documento, e o botão exige rolagem vertical para ser alcançado. |
| **04. Aprender** | O conteúdo gerado é confortável de ler (espaçamento, escaneabilidade) e a opção de exportar é fácil de localizar | ✅ | Cards dedicados para flashcards, passo a passo, TL;DR e quiz interativo, com seção clara de exportação e feedback. *(Validação visual com conteúdo real gerado recomendada em próximo teste.)* |

*Legenda: ✅ Adequado | ⚠️ Precisa de melhoria | ❌ Inadequado | ⬜ Não avaliado*

### Componentes, Fluidez e Tom de Voz (UX Writing)
* [x] **Botões com verbos claros:** CTAs bem redigidos (*"Criar Conteúdo no Estúdio"*, *"Gerenciar Biblioteca"*, *"Adicionar à Biblioteca"*, *"Salvar Texto como .txt"*). Recomenda-se apenas encurtar o CTA da home para evitar corte (`...`).
* [ ] **Fluidez de navegação:** **Prejudicada por arquitetura do Streamlit.** Chamadas de `st.rerun()` e `on_change="rerun"` reexecutam todo o script Python ao trocar de aba, selecionar formato ou adicionar documento, gerando micro-travamentos perceptíveis.
* [ ] **Tom de voz da marca:** **Ponto de melhoria prioritário.** Excesso de jargão técnico de infraestrutura (`Contrato v0.3`, `POST /geracoes`, `GET /quiz`, `multipart/form-data`, `SQLite`, `usuario_id`, `OCI SDK/PAR` e URL do Render) disputando atenção com a experiência de aprendizagem.
* [x] **Mensagens de erro objetivas:** Validações de extensão, arquivo vazio, limite de 20 MiB e campos vazios explicam claramente o problema; erros de API exibem `mensagem_amigavel` e mantêm detalhes técnicos recolhidos.

---

## 4. Estados da Interface

* [x] **Estado Vazio (*Empty State*):** Implementado em todas as 4 telas (*Visão geral*, *Minha biblioteca*, *Estúdio de criação* e *Meus conteúdos*), orientando o próximo passo — porém, no Estúdio, a coluna vazia cria desproporção visual frente à coluna de parâmetros.
* [x] **Estado de Carregamento (*Loading*):** Uso de `st.status` com etapas progressivas e desabilitação imediata do botão (`⏳ Gerando conteúdo...`).
* [x] **Estados de Sucesso e Erro:** Feedbacks claros com ícones (`✅`, `❌`, `⚠️`) próximos às ações executadas.
* [ ] **Transições e Micro-interações:** Hover e área mínima de toque (`44px`) funcionam bem, mas os *reruns* completos de página criam piscadas/travamentos rápidos entre interações simples.

---

## 5. Acessibilidade (WCAG AA) e Responsividade

* [x] **Contraste em cores pastéis — Modo Claro (Regra Crítica):** **Aprovado.** Nenhum texto branco sobre menta, lilás ou rosa pastel; botões primários usam `#1B3B2B` sobre `#A8E6CF` (contraste $> 8.5:1$).
* [ ] **Contraste e visibilidade — Modo Escuro (Regra Crítica):** **Reprovado.** Tags `<code>` (ex.: nome do bucket na sidebar) renderizam texto claro (`#F8FAFC`) sobre fundo branco herdado do tema base claro, tornando o conteúdo invisível; mascote e textos auxiliares também perdem visibilidade no Dark Mode.
* [x] **Independência de cor:** **Aprovado.** Alertas, status da API (`🟢 API Online` / `🔴 API Offline`) e mensagens combinam cor + ícone + texto.
* [ ] **Navegação por teclado:** **Requer ajuste.** Ausência de regra `:focus-visible` no CSS customizado; o foco nativo do Streamlit em tom menta claro tem baixo contraste sobre superfícies claras.
* [ ] **Responsividade (Mobile):** **Parcialmente validado (via código).** Boas regras `@media (max-width: 768px)` (`initial_sidebar_state="auto"`, `min-height: 44px`, reordenamento do hero), mas requer **teste prático em smartphone real (`390×844`)**.

---

## 6. Registro de Inconsistências de UX/UI

| ID | Categoria | Severidade | Tela / Componente | Esperado (Brandbook) | Encontrado (Streamlit) | Evidência | Status |
| :---: | :---: | :---: | :--- | :--- | :--- | :---: | :---: |
| `A11Y-02` | Acessibilidade / Visual | 🔴 Crítico | Global — Modo Escuro (Sidebar `<code>`, Mascote e textos nativos) | Leitura confortável e contraste WCAG AA ($\ge 4.5:1$) em todos os elementos, com marca/mascote visíveis | Conflito entre `base = "light"` no `config.toml` e CSS Dark Mode: texto branco sobre fundo branco em tags `<code>` (nome do bucket invisível) e mascote/elementos perdendo visibilidade no escuro | PDFs Dark Mode `00` a `03` (p. 1–2) / `main.py` | Aberto |
| `A11Y-01` | Acessibilidade | 🟠 Alto | Global (Botões, Inputs, Radios) | Foco visível ao navegar via teclado com contraste adequado | Ausência de regra `:focus-visible` no CSS customizado; anel de foco claro (`#A8E6CF`) pouco perceptível sobre fundo branco | `main.py` (bloco `<style>`) | Aberto |
| `UX-01` | UX Writing | 🟠 Alto | Todas as telas (Sidebar, Estúdio, Biblioteca, Meus conteúdos) | Tom simples, didático e acolhedor, sem sobrecarga técnica | Exposição de `Contrato v0.3: POST /geracoes (multipart/form-data)`, `GET /quiz`, `SQLite`, `usuario_id`, bucket OCI e URL crua do Render dividindo atenção com o estudo | PDFs Light & Dark / `main.py` | Aberto |
| `UX-04` | Usabilidade / Performance | 🟠 Alto | Global (Navegação, Abas, Upload e Seleção de Formato) | Interações fluidas e leves sem sensação de travamento | Reruns totais de página (`st.rerun()` e `on_change="rerun"`) reexecutam todo o script Python, gerando micro-paralisações perceptíveis ao estudante | `main.py` (linhas de navegação, abas e botões) | Aberto |
| `UI-04` | Visual / Layout | 🟡 Médio | Estúdio de criação (Colunas Esquerda e Direita) | Distribuição equilibrada que privilegie a ação principal sem rolagem excessiva | Coluna esquerda muito longa (empurra o botão *"Gerar"* para baixo da dobra), enquanto a coluna direita fica com grande espaço vazio sem conteúdo ativo | PDFs Estúdio (p. 1–2) | Aberto |
| `UX-05` | Usabilidade / Visual | 🟡 Médio | Estúdio de criação (Seção `02 · Formato pedagógico`) | Experiência criativa, visual e envolvente | Seleção dos 6 formatos pedagógicos via `st.radio` vertical clássico, resultando em lista longa, linear e monótona | PDFs Estúdio (p. 2) / `main.py` | Aberto |
| `UI-01` | Visual / Layout | 🟡 Médio | Visão geral (CTA) e Estúdio (Selectboxes `p1, p2`) | Textos legíveis sem corte em botões e campos de formulário | Botão truncado (`✦ Criar Conteúdo no Est...`) e *selectboxes* cortados (`Iniciante / ...`, `Básico (Did...`) em larguras intermediárias | PDFs Visão geral e Estúdio (p. 1) | Aberto |
| `UI-02` | Visual / Layout | 🟡 Médio | Sidebar (Todas as telas) | Sidebar discreta e enxuta, sem excesso de estímulos | Bloco `st.success` com URL longa da API + painel de identidade + rodapé alongam a sidebar, exigindo rolagem | PDFs Light & Dark (p. 1–2) | Aberto |
| `UX-02` | Usabilidade | 🟡 Médio | Estúdio de criação (Estado sem documento) | Jornada fluida guiando o usuário ao primeiro passo | Alerta informa para ir à *Minha biblioteca*, mas sem botão de atalho direto; usuário precisa voltar manualmente pela sidebar | PDFs Estúdio (p. 1) / `main.py` | Aberto |
| `UI-03` | Visual / Tipografia | 🔵 Baixo | Páginas 2, 3 e 4 (`st.title`) | Títulos de página entre `28–32px` (`semibold`) | `st.title()` renderiza no padrão Streamlit (~44px), maior que o `h1` do Hero (~30px) | PDFs Páginas 2, 3 e 4 | Aberto |
| `UX-03` | UX Writing | 🔵 Baixo | Estúdio de criação (Empty state à direita) | Consistência entre instruções e rótulos dos botões | Texto orienta clicar em `'Gerar Conteúdo'` para *"consultar a API real"*, mas o botão se chama `'✦ Gerar Conteúdo Educacional com IA'` | PDFs Estúdio (p. 1) / `main.py` | Aberto |

*Categorias: `Visual` | `Usabilidade` | `Acessibilidade` | `UX Writing` | `Responsividade` | `Performance`*
*Severidade: 🔴 Crítico (impede leitura/uso) | 🟠 Alto | 🟡 Médio | 🔵 Baixo (ajuste fino)*

---

## 7. Sugestões de Melhoria de UX/UI

### ⚡ Quick Wins (Ajustes Rápidos no `main.py`)
*Melhorias de alto impacto que podem ser aplicadas rapidamente via CSS, troca de widgets nativos do Streamlit e ajuste de microcopy:*

1. **Corrigir bugs críticos do Modo Escuro (`A11Y-02`):**
   * Estilizar explicitamente todas as tags `code` no CSS global: `code { background-color: var(--color-surface-alt) !important; color: var(--color-text) !important; padding: 2px 6px; border-radius: 6px; }`.
   * Garantir contraste do mascote no Dark Mode usando fundo claro suave no container (como já é feito no logotipo com `--color-logo-box: #F8FAFC`) ou adicionar um halo/card claro ao redor do mascote também no *empty state* do Estúdio.
   * Sobrescrever explicitamente as cores de fundo e texto dos alertas nativos (`[data-testid="stAlert"]`) para respeitarem `--color-surface-alt` e `--color-text` no Dark Mode.
2. **Tornar a seleção de formatos mais visual e compactar o Estúdio (`UX-05` e `UI-04`):**
   * Substituir `st.radio` vertical por `st.pills` ou `st.segmented_control` (ou `st.radio(..., horizontal=True)` com rótulos mais curtos e ícones), reduzindo drasticamente a altura da coluna esquerda e trazendo o botão **"Gerar Conteúdo"** para a primeira dobra da tela.
3. **Reduzir sobrecarga técnica na interface (`UX-01`):**
   * Mover o aviso do `Contrato v0.3` (`POST /geracoes`, `multipart/form-data`), a URL da API e o nome do bucket OCI para um `st.expander("ℹ️ Detalhes técnicos")` discreto no rodapé da sidebar.
   * Renomear a aba `"🎯 Quizzes salvos no servidor (GET /quiz)"` para `"🎯 Quizzes salvos"`.
4. **Adicionar foco visível acessível (`A11Y-01`):**
   * Incluir no `<style>` uma regra `:focus-visible` com alto contraste: `outline: 3px solid var(--color-eyebrow) !important; outline-offset: 2px;`.
5. **Corrigir truncamentos, tipografia e atalho (`UI-01`, `UX-02`, `UI-03`, `UX-03`):**
   * Encurtar o CTA da home para `"✦ Criar conteúdo"`, empilhar os *selectboxes* do Estúdio para evitar corte de texto, padronizar `h1 { font-size: 1.85rem !important; }` e adicionar um botão `"📂 Ir para Minha biblioteca"` logo abaixo do aviso de biblioteca vazia no Estúdio.
6. **Amenizar micro-travamentos no Streamlit (`UX-04`):**
   * Adotar `@st.fragment` (recurso nativo do Streamlit $\ge 1.37$) em blocos isolados — como formulário de parâmetros do Estúdio, prévia de documentos e rodadas do Quiz — para evitar que interações locais disparem o rerun completo da página.

### ✨ Evoluções de UX e Arquitetura (Pós-MVP)
*Ideias para superar limitações estruturais do Streamlit e elevar a experiência em versões futuras:*

1. **Redesenho do fluxo do Estúdio de Criação:** Adotar um painel de configuração colapsável (*drawer* ou barra superior em passos) para que, após gerar o conteúdo, a área de leitura/estudo ocupe 100% da largura com foco total.
2. **Cards visuais clicáveis para formatos pedagógicos:** Substituir seletores padrão por cards ilustrados com mini-descrição de cada formato (ex.: *"Quiz: teste seus conhecimentos em 3 rodadas"*, *"Flashcards: revisão rápida"*).
3. **Indicador de progresso (*stepper*) da jornada:** Barra discreta no topo indicando o estágio atual (`1. Fontes` → `2. Personalizar` → `3. Gerar` → `4. Aprender`).
4. **Migração de frontend para eliminar limitações do Streamlit:** Caso o produto evolua além do hackathon, migrar a camada visual para um frontend dedicado (ex.: React / Next.js consumindo a mesma API FastAPI) para eliminar reruns totais de página, ganhar controle absoluto sobre o Design System/Dark Mode e criar micro-interações fluidas.

---

## 8. Evidências Visuais

> Capturas de tela salvas em `docs/design/qa/evidencias/` (em PNG):

* **Modo Claro (Desktop):**
  * Visão Geral: `![Visão Geral - Light](./evidencias/visao-geral-light.png)` *(inserir evidência)*
  * Minha Biblioteca: `![Minha Biblioteca - Light](./evidencias/minha-biblioteca-light.png)` *(inserir evidência)*
  * Estúdio de Criação: `![Estúdio de Criação - Light](./evidencias/estudio-criacao-light.png)` *(inserir evidência)*
  * Meus Conteúdos: `![Meus Conteúdos - Light](./evidencias/meus-conteudos-light.png)` *(inserir evidência)*
* **Modo Escuro (Desktop):**
  * Visão Geral & Bug `<code>` na Sidebar: `![Dark Mode - Sidebar Code Bug](./evidencias/dark-mode-sidebar-code.png)`
  * Estúdio de Criação (Dark Mode / Layout assimétrico): `![Estúdio - Dark](./evidencias/estudio-criacao-dark.png)` *(inserir evidência)*
* **Validação Mobile (`390×844`):** `*(Pendente de captura em dispositivo real / DevTools)*` *(inserir evidência)*
