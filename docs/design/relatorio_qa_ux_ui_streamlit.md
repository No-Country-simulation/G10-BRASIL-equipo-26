# 🎨 Relatório de Auditoria Design QA — Streamlit

> **Projeto:** MentorIA Tech (Desafio NovaMente) | Hackathon ONE — Grupo 10 (Equipe 26)
> **Referência Oficial:** [Guia de Design (`design.md`)](../design/design.md) | [Brandbook UX/UI](../design/MentorIA-Tech_Brandbook_UXUI.pdf)

Este documento registra a auditoria de **Design QA** da aplicação deployada no Streamlit, avaliando a fidelidade visual ao Brandbook, usabilidade da jornada, acessibilidade (WCAG AA), UX Writing e qualidade da experiência do usuário, com base na análise do código-fonte (`main.py` e `.streamlit/config.toml`) e nas capturas das 4 telas principais.

---

## 📋 Informações da Avaliação

| Campo | Detalhes |
| :--- | :--- |
| **URL da Aplicação (Streamlit)** | `https://mentoria-tech-ai.streamlit.app/` |
| **Data da Avaliação** | `18/11/2026` |
| **Avaliador(a) UX/UI** | `Lysara Pinheiro / @LysaJPDataLab` |
| **Escopo Analisado** | Código (`main.py`, `.streamlit/config.toml`) + Telas exportadas (Visão geral, Minha biblioteca, Estúdio de criação, Meus conteúdos) |
| **Dispositivos / Viewports** | Desktop (paisagem via exportação) + Revisão de regras `@media (max-width: 768px)` no código *(teste interativo em mobile real pendente)* |
| **Status Geral de UX/UI** | 🟡 **Aprovado com ressalvas** (alta fidelidade visual e excelente contraste; requer ajustes pontuais de UX Writing, foco de teclado e compactação de layout) |

---

## 1. Resumo Executivo de UX/UI

*Síntese sobre a percepção geral da interface (clareza, leveza, autonomia e consistência visual):*

* **O que funciona muito bem:**
  * **Fidelidade à paleta e tokens:** O `.streamlit/config.toml` e as variáveis CSS de `main.py` aplicam com precisão a paleta pastel (`#A8E6CF`, `#CDB4DB`, `#FFC8DD`), os fundos claros (`#FAFAFC` e `#FFFFFF`), a fonte `Inter` com fallback métrico e os raios de borda (`16px` em cards e `10px` em controles).
  * **Acessibilidade de contraste (WCAG AA/AAA):** O código resolve proativamente o problema clássico de botões pastéis no Streamlit, forçando texto escuro (`#1B3B2B` / `#293241`) sobre Verde Menta e Lavanda Clara, além de escurecer o texto secundário (`#4A5568`) para garantir contraste $\ge 4.5:1$.
  * **Modo Escuro bem resolvido:** A implementação de Dark Mode protege o logotipo com um container claro (`--color-logo-box: #F8FAFC`), respeitando a diretriz de fundo prioritário claro do Brandbook.
  * **Estados bem tratados:** Estados vazios (*empty states*) acolhedores em todas as telas, feedback de carregamento passo a passo (`st.status`) com botão desabilitado durante a geração e erros amigáveis com detalhes técnicos recolhidos.

* **Principais pontos de atrito:**
  * **Excesso de jargão técnico na interface (UX Writing):** Termos como `multipart/form-data`, `POST /geracoes`, `GET /quiz`, `Contrato v0.3`, `SQLite`, `OCI SDK/PAR` e a URL crua do Render aparecem em áreas nobres da interface, destoando do tom de voz acolhedor e didático do Brandbook.
  * **Foco de teclado (`:focus-visible`) sem estilo dedicado:** Não há regra explícita de foco visível no CSS customizado; como `primaryColor` é um verde menta claro, o anel de foco nativo pode ficar pouco perceptível sobre fundos brancos.
  * **Sidebar extensa e truncamento em colunas estreitas:** A barra lateral exige rolagem vertical devido ao bloco de status da API com URL longa e ao rodapé; além disso, o CTA da *Visão geral* e os *selectboxes* lado a lado no *Estúdio de criação* sofrem truncamento em larguras intermediárias.

---

## 2. Auditoria de Identidade Visual (Aderência ao Brandbook)

### Logotipo e Marca
* [x] **Fundo prioritário:** Logotipo aplicado sobre fundo claro na sidebar (`transparent` no modo claro sobre `#FFFFFF` e `#F8FAFC` no modo escuro).
* [x] **Área de respiro:** Container `.nm-brand-container` aplica `padding: 12px` e recorte controlado com `padding=12` no processamento da imagem, preservando margem limpa ao redor da marca.
* [x] **Integridade:** Dimensões proporcionais preservadas com `aspect-ratio` explícito e sem distorção cromática.

### Paleta de Cores e Superfícies
* [x] **Fundos e superfícies:** Off-white (`#FAFAFC`) no fundo geral e Branco (`#FFFFFF`) nos cards (`stVerticalBlockBorderWrapper`) e sidebar.
* [x] **Cores de destaque:** Verde Menta (`#A8E6CF`) nas ações primárias e item ativo do menu; Lavanda/Lilás (`#EDE4F5` / `#CDB4DB`) nas ações secundárias e badges; Rosa Suave (`#FFC8DD` / `#FFF0F5`) no gradiente do hero e pills.
* [x] **Hierarquia antes de decoração:** Superfícies claras predominam e organizam bem o conteúdo; há apenas leve poluição visual na sidebar causada pelo alerta verde `st.success` com a URL completa da API.

### Tipografia e Espaçamento
* [x] **Família tipográfica:** `Inter` carregada via Google Fonts com `@font-face` de fallback métrico (`Inter Fallback`, `system-ui`), minimizando *layout shift* (CLS).
* [ ] **Escala e hierarquia:** `.nm-hero h1` (`1.85rem` / ~30px) e `.nm-section-title` (`1.28rem` / ~20px) seguem o Brandbook, mas `st.title()` nas páginas 2, 3 e 4 mantém o tamanho padrão do Streamlit (~44px), criando leve inconsistência de escala entre a *Visão geral* e as demais telas.
* [x] **Geometria e layout:** Cards com `border-radius: 16px`, controles com `10px`, sombras suaves e bordas sutis (`#E5E7EB`, ajuste positivo sobre `#F1F3F5` para melhor definição de cards).
* [ ] **Estrutura de tela:** Conteúdo central amplo e painéis contextuais bem organizados, porém a **sidebar está verticalmente longa**, ultrapassando uma dobra de tela em notebooks padrão.

---

## 3. Usabilidade, Jornada e UX Writing

### Clareza da Jornada (4 Etapas)
| Etapa | Critério de Experiência Avaliado | Status | Observações |
| :--- | :--- | :---: | :--- |
| **01. Fontes** | Área de upload/inserção de texto é intuitiva e indica claramente os formatos aceitos (PDF, MD, texto) | ✅ | Excelente oferta de 3 caminhos: upload, PDF de exemplo real (`Machine_Learning.pdf`) e texto manual. Único ajuste é simplificar a menção a `multipart/form-data`. |
| **02. Personalizar** | Campos de perfil, nicho e formato são fáceis de preencher e possuem rótulos (*labels*) persistentes | ⚠️ | Rótulos persistentes OK, mas `Perfil do Destinatário` e `Nível de Profundidade` em 2 colunas dentro do card esquerdo truncam os textos selecionados (`Iniciante / ...`, `Básico (Did...`). |
| **03. Gerar** | Ação principal é evidente e o tempo de espera oferece feedback visual claro de progresso | ⚠️ | Ótimo `st.status` com etapas e proteção contra duplo clique. Porém, quando não há documento carregado, o aviso não oferece um botão de atalho direto para *Minha biblioteca*, e a nota técnica *"Contrato v0.3"* compete visualmente com o botão principal. |
| **04. Aprender** | O conteúdo gerado é confortável de ler (espaçamento, escaneabilidade) e a opção de exportar é fácil de localizar | ✅ | Cards dedicados para flashcards, passo a passo, TL;DR e quiz interativo, com seção clara de exportação e bloco de feedback logo abaixo. *(Validação visual com conteúdo real gerado recomendada em próximo teste.)* |

*Legenda: ✅ Adequado | ⚠️ Precisa de melhoria | ❌ Inadequado | ⬜ Não avaliado*

### Componentes e Tom de Voz (UX Writing)
* [x] **Botões com verbos claros:** CTAs bem redigidos (*"Criar Conteúdo no Estúdio"*, *"Gerenciar Biblioteca"*, *"Adicionar à Biblioteca"*, *"Salvar Texto como .txt"*). Apenas recomenda-se encurtar o CTA da home para evitar reticências (`...`).
* [ ] **Tom de voz da marca:** **Ponto de melhoria prioritário.** Embora o hero e os estados vazios sejam acolhedores, há excesso de jargão técnico de infraestrutura voltado a desenvolvedores (`POST /geracoes`, `GET /quiz`, `multipart/form-data`, `SQLite`, `usuario_id`, `Contrato v0.3`, `OCI SDK/PAR`).
* [x] **Mensagens de erro objetivas:** Validações de extensão, arquivo vazio, limite de 20 MiB e campos vazios explicam claramente o problema; erros de API exibem `mensagem_amigavel` e escondem o stack/detalhe técnico em um `st.expander`.

---

## 4. Estados da Interface

* [x] **Estado Vazio (*Empty State*):** Implementado em todas as 4 telas (*Visão geral*, *Minha biblioteca*, *Estúdio de criação* com mascote ilustrativo e *Meus conteúdos*), sempre orientando o próximo passo.
* [x] **Estado de Carregamento (*Loading*):** Uso de `st.status` com mensagens progressivas e desabilitação imediata do botão (`⏳ Gerando conteúdo...`) via callback.
* [x] **Estados de Sucesso e Erro:** Feedbacks claros com ícones (`✅`, `❌`, `⚠️`) próximos às ações executadas.
* [x] **Estados de Interação:** Hover com leve elevação/sombra nos botões primários e secundários, além de área mínima de toque (`min-height: 44px`).

---

## 5. Acessibilidade (WCAG AA) e Responsividade

* [x] **Contraste em cores pastéis (Regra Crítica):** **Aprovado.** Nenhum texto branco sobre menta, lilás ou rosa pastel. Botões primários usam `#1B3B2B` sobre `#A8E6CF` (contraste > 8.5:1) e secundários usam `#293241` sobre `#EDE4F5`.
* [x] **Legibilidade de textos secundários:** **Aprovado.** `--color-text-muted` foi ajustado para `#4A5568` (modo claro) e `#CBD5E1` (modo escuro), garantindo WCAG AA ($\ge 4.5:1$).
* [x] **Independência de cor:** **Aprovado.** Alertas, status da API (`🟢 API Online` / `🔴 API Offline`) e mensagens combinam cor + ícone + texto.
* [ ] **Navegação por teclado:** **Requer ajuste.** O CSS customizado não define regra `:focus-visible` para botões, inputs e seletores; o foco nativo do Streamlit em tom menta claro pode ter baixo contraste sobre superfícies claras.
* [ ] **Responsividade (Mobile):** **Parcialmente validado (via código).** Há boas regras `@media (max-width: 768px)` (reordenamento do hero, redução do mascote, `initial_sidebar_state="auto"`, `min-height: 44px`), porém requer **teste prático em viewport mobile real (`390×844`)** para confirmar ausência de rolagem horizontal em tabelas/selects.

---

## 6. Registro de Inconsistências de UX/UI

| ID | Categoria | Severidade | Tela / Componente | Esperado (Brandbook) | Encontrado (Streamlit) | Evidência | Status |
| :---: | :---: | :---: | :--- | :--- | :--- | :---: | :---: |
| `A11Y-01` | Acessibilidade | 🟠 Alto | Global (Botões, Inputs, Radios) | Foco visível ao navegar via teclado com contraste adequado | Ausência de regra `:focus-visible` no CSS customizado; risco de anel de foco claro (`#A8E6CF`) sobre fundo branco | `main.py` (bloco `<style>`) | Aberto |
| `UX-01` | UX Writing | 🟠 Alto | Todas as telas (Sidebar, Hero, Estúdio, Meus conteúdos) | Tom didático, simples e sem excesso de jargão técnico | Exposição de `POST /geracoes`, `GET /quiz`, `multipart/form-data`, `Contrato v0.3`, `SQLite`, `usuario_id` e URL crua do Render | PDFs 1 a 4 / `main.py` | Aberto |
| `UI-01` | Visual / Layout | 🟡 Médio | Visão geral (CTA) e Estúdio (Selectboxes `p1, p2`) | Textos legíveis sem corte em botões e campos de formulário | Botão truncado (`✦ Criar Conteúdo no Est...`) e selectboxes cortados (`Iniciante / ...`, `Básico (Did...`) em larguras intermediárias | PDF 2 (p. 1) e PDF 4 (p. 1) | Aberto |
| `UI-02` | Visual / Layout | 🟡 Médio | Sidebar (Todas as telas) | Sidebar discreta e enxuta, sem excesso de estímulos | Bloco `st.success` com URL longa da API + rodapé + painel de identidade alongam a sidebar, exigindo rolagem | PDFs 1 a 4 (p. 1–2) | Aberto |
| `UX-02` | Usabilidade | 🟡 Médio | Estúdio de criação (Estado sem documento) | Jornada fluida guiando o usuário ao primeiro passo | Alerta informa para ir à *Minha biblioteca*, mas sem botão de atalho direto; usuário precisa localizar o item na sidebar | PDF 2 (p. 1) / `main.py` | Aberto |
| `UI-03` | Visual / Tipografia | 🔵 Baixo | Páginas 2, 3 e 4 (`st.title`) | Títulos de página entre `28–32px` (`semibold`) | `st.title()` renderiza no padrão Streamlit (~44px), maior que o `h1` do Hero (`~30px`) | PDFs 1, 2 e 3 | Aberto |
| `UX-03` | UX Writing | 🔵 Baixo | Estúdio de criação (Empty state à direita) | Consistência entre instruções e rótulos dos botões | Texto orienta clicar em `'Gerar Conteúdo'` para *"consultar a API real"*, mas o botão se chama `'✦ Gerar Conteúdo Educacional com IA'` | PDF 2 (p. 1) / `main.py` | Aberto |

*Categorias: `Visual` | `Usabilidade` | `Acessibilidade` | `UX Writing` | `Responsividade`*
*Severidade: 🔴 Crítico (prejudica leitura/uso) | 🟠 Alto | 🟡 Médio | 🔵 Baixo (ajuste fino)*

---

## 7. Sugestões de Melhoria de UX/UI

### ⚡ Quick Wins (Ajustes Rápidos no `main.py`)
*Melhorias de alto impacto que podem ser aplicadas em poucos minutos via CSS ou ajuste de microcopy:*

1. **Adicionar foco visível acessível (`A11Y-01`):** Incluir no `<style>` uma regra `:focus-visible` com borda de alto contraste (`outline: 3px solid var(--color-eyebrow) !important; outline-offset: 2px;`) para botões, inputs e controles interativos.
2. **Suavizar o jargão técnico na interface (`UX-01`):**
   * Substituir o bloco grande de `st.success` da sidebar por uma pílula compacta (`🟢 Serviço conectado`) e mover a URL da API, bucket OCI e detalhes do `Contrato v0.3` para um `st.expander("ℹ️ Detalhes técnicos")` discreto no rodapé da sidebar.
   * Renomear a aba `"🎯 Quizzes salvos no servidor (GET /quiz)"` para `"🎯 Quizzes salvos"`.
   * Trocar *"via `multipart/form-data` ao pipeline RAG da API"* por *"Envie seus materiais técnicos em PDF, Markdown ou Texto (até 20 MB) para gerar conteúdos personalizados."*.
3. **Corrigir truncamento de textos (`UI-01`):**
   * Encurtar o CTA principal da *Visão geral* para `"✦ Criar conteúdo"` (alinhado ao exemplo do Brandbook) e garantir `white-space: normal !important;` também em `div.stButton > button p`.
   * No *Estúdio de criação*, empilhar `Perfil do Destinatário` e `Nível de Profundidade` em linhas separadas (ou aumentar a proporção da coluna esquerda) para evitar corte nos nomes dos perfis.
4. **Adicionar botão de atalho no Estúdio vazio (`UX-02`):** Logo abaixo do `st.warning` de biblioteca vazia, exibir um botão secundário `"📂 Carregar documento na Biblioteca"` que chama `navegar_para("Minha biblioteca")`.
5. **Padronizar tamanho de `st.title()` (`UI-03`) e alinhar microcopy (`UX-03`):** Definir `h1 { font-size: 1.85rem !important; font-weight: 700 !important; }` no CSS global e atualizar o texto do empty state do Estúdio para referenciar o nome exato do botão.

### ✨ Evoluções de UX (Pós-MVP)
*Ideias para elevar a experiência em versões futuras:*

1. **Indicador visual de progresso (*stepper*) da jornada:** Exibir uma barra discreta no topo indicando o estágio atual do usuário (`1. Fontes` → `2. Personalizar` → `3. Gerar` → `4. Aprender`).
2. **Ação rápida de upload dentro do Estúdio:** Permitir arrastar um arquivo ou carregar o PDF de exemplo diretamente no *Estúdio de criação* quando a biblioteca estiver vazia, reduzindo a troca de telas.
3. **Validação em dispositivos móveis reais e Lighthouse pós-ajustes:** Executar uma bateria final de testes em smartphone (`390×844`) cobrindo também as telas **com conteúdo gerado** (Quiz em andamento, Flashcards e Exportação).

---

## 8. Evidências Visuais

> Recomenda-se salvar as capturas de tela em `docs/qa/evidencias/` (em PNG, preferencialmente sem compressão de impressão em PDF) e vincular abaixo:

* **Tela 1 — Visão Geral (Desktop):** `![Visão Geral](./evidencias/visao-geral-desktop.png)` *(analisada via PDF exportado)*
* **Tela 2 — Minha Biblioteca (Desktop):** `![Minha Biblioteca](./evidencias/minha-biblioteca-desktop.png)` *(analisada via PDF exportado)*
* **Tela 3 — Estúdio de Criação (Desktop):** `![Estúdio de Criação](./evidencias/estudio-criacao-desktop.png)` *(analisada via PDF exportado)*
* **Tela 4 — Meus Conteúdos (Desktop):** `![Meus Conteúdos](./evidencias/meus-conteudos-desktop.png)` *(analisada via PDF exportado)*
* **Validação Mobile (`390×844`):** `*(Pendente de captura em dispositivo real / DevTools)*`
