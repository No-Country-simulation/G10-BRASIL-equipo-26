# 🎨 Relatório Design QA

> **Projeto:** MentorIA Tech (Desafio NovaMente) | Hackathon ONE — Grupo 10 (Equipe 26)
> **Referência Oficial:** [Guia de Design (`design.md`)](../design/design.md) | [Brandbook UX/UI](../design/MentorIA-Tech_Brandbook_UXUI.pdf)

Este documento registra a auditoria de **Design QA** da aplicação deployada no Streamlit, avaliando a fidelidade visual ao Brandbook, usabilidade da jornada, acessibilidade (WCAG AA) e qualidade da experiência do usuário.

---

## 📋 Informações da Avaliação

| Campo | Detalhes |
| :--- | :--- |
| **URL da Aplicação (Streamlit)** | `[Inserir link do deploy]` |
| **Data da Avaliação** | `DD/MM/2026` |
| **Avaliador(a) UX/UI** | `[Seu nome / GitHub]` |
| **Dispositivos / Viewports Testados** | Ex.: Desktop (`1440×900` / `1920×1080`) e Mobile (`390×844`) |
| **Navegadores** | Ex.: Chrome, Safari |
| **Status Geral de UX/UI** | 🟡 Requer ajustes visuais / 🟢 Aprovado / 🔴 Problemas críticos de usabilidade |

---

## 1. Resumo Executivo de UX/UI

*Síntese rápida sobre a percepção geral da interface (clareza, leveza, autonomia e consistência visual):*

* **O que funciona bem:** `[Ex.: Hierarquia de leitura clara, fluxo de etapas fácil de entender...]`
* **Principais pontos de atrito:** `[Ex.: Contraste insuficiente nos botões padrão do Streamlit, falta de espaçamento entre cards no mobile...]`

---

## 2. Auditoria de Identidade Visual (Aderência ao Brandbook)

### Logotipo e Marca
* [ ] **Fundo prioritário:** Logotipo aplicado sobre fundo claro (`#FFFFFF` ou `#FAFAFC`), garantindo contraste e leitura.
* [ ] **Área de respiro:** Margem mínima equivalente a `1M` preservada ao redor da marca, sem elementos colados.
* [ ] **Integridade:** Cores originais dos nós (menta, lilás e rosa) mantidas sem distorção de proporção.

### Paleta de Cores e Superfícies
* [ ] **Fundos e superfícies:** Aplicação utiliza Off-white (`#FAFAFC`) no fundo geral e Branco (`#FFFFFF`) nos cards/áreas de leitura.
* [ ] **Cores de destaque:** Verde Menta (`#A8E6CF`) usado para ações primárias, Lilás Pastel (`#CDB4DB`) para secundárias e Rosa Suave (`#FFC8DD`) para destaques sutis.
* [ ] **Hierarquia antes de decoração:** Superfícies claras predominam, evitando excesso de estímulos visuais.

### Tipografia e Espaçamento
* [ ] **Família tipográfica:** Fonte *sans-serif* limpa (`Inter` ou `system-ui`) aplicada de forma consistente.
* [ ] **Escala e hierarquia:** Diferença visual clara entre Títulos (`28–32px`), Subtítulos (`18–22px`) e Corpo de texto (`14–16px`).
* [ ] **Geometria e layout:** Cards com cantos arredondados (`16px`), controles/botões padronizados (`10px`) e divisórias sutis (`#F1F3F5`).
* [ ] **Estrutura de tela:** Sidebar discreta + conteúdo central amplo + painéis contextuais bem alinhados.

---

## 3. Usabilidade, Jornada e UX Writing

### Clareza da Jornada (4 Etapas)
| Etapa | Critério de Experiência Avaliado | Status | Observações |
| :--- | :--- | :---: | :--- |
| **01. Fontes** | Área de upload/inserção de texto é intuitiva e indica claramente os formatos aceitos (PDF, MD, texto) | ⬜ | |
| **02. Personalizar** | Campos de perfil, nicho e formato são fáceis de preencher e possuem rótulos (*labels*) persistentes | ⬜ | |
| **03. Gerar** | Ação principal é evidente e o tempo de espera oferece feedback visual claro de progresso | ⬜ | |
| **04. Aprender** | O conteúdo gerado é confortável de ler (espaçamento, escaneabilidade) e a opção de exportar é fácil de localizar | ⬜ | |

*Legenda: ✅ Adequado | ⚠️ Precisa de melhoria | ❌ Inadequado | ⬜ Não avaliado*

### Componentes e Tom de Voz (UX Writing)
* [ ] **Botões com verbos claros:** CTAs indicam exatamente o que fazem (ex.: *"Criar conteúdo"*, *"Exportar"*), sem termos genéricos.
* [ ] **Tom de voz da marca:** Textos simples (sem infantilizar), didáticos (sem excesso de jargão) e encorajadores na medida certa.
* [ ] **Mensagens de erro objetivas:** Quando algo falha ou falta preencher um campo, o texto explica o problema e como resolver.

---

## 4. Estados da Interface

* [ ] **Estado Vazio (*Empty State*):** Antes de gerar qualquer material, a tela orienta o usuário sobre o primeiro passo (não parece "quebrada" ou em branco).
* [ ] **Estado de Carregamento (*Loading*):** Feedback visual explicativo durante o processamento, evitando sensação de travamento.
* [ ] **Estados de Sucesso e Erro:** Feedback claro e posicionado próximo à ação executada.
* [ ] **Estados de Interação:** Hover, clique e seleção de itens são visualmente perceptíveis.

---

## 5. Acessibilidade (WCAG AA) e Responsividade

* [ ] **Contraste em cores pastéis (Regra Crítica):** **Nenhum** texto branco (`#FFFFFF`) sobre menta (`#A8E6CF`), lilás (`#CDB4DB`) ou rosa pastel (`#FFC8DD`) — texto em Grafite (`#293241`) garantido.
* [ ] **Legibilidade de textos secundários:** Textos de apoio (`#657080`) mantêm contraste legível sobre fundos claros.
* [ ] **Independência de cor:** Estados de sucesso, alerta, erro ou seleção não dependem apenas da cor (acompanham texto ou ícone).
* [ ] **Navegação por teclado:** É possível percorrer campos e botões com `Tab` mantendo o foco visível.
* [ ] **Responsividade (Mobile):** Leitura confortável em telas pequenas, sem rolagem horizontal indesejada, sobreposição de textos ou botões difíceis de tocar.

---

## 6. Registro de Inconsistências de UX/UI

| ID | Categoria | Severidade | Tela / Componente | Esperado (Brandbook) | Encontrado (Streamlit) | Evidência | Status |
| :---: | :---: | :---: | :--- | :--- | :--- | :---: | :---: |
| `UI-01` | Acessibilidade | 🔴 Crítico | Botão Primário ("Gerar") | Texto em Grafite (`#293241`) sobre Verde Menta (`#A8E6CF`) | Texto branco herdado do padrão do Streamlit | `[print](./evidencias/ui-01.png)` | Aberto |
| `UX-01` | Usabilidade | 🟡 Médio | Área de Upload | Estado vazio explicando o que fazer | Área em branco sem orientação inicial | `[print](./evidencias/ux-01.png)` | Aberto |

*Categorias: `Visual` | `Usabilidade` | `Acessibilidade` | `UX Writing` | `Responsividade`*
*Severidade: 🔴 Crítico (prejudica leitura/uso) | 🟠 Alto | 🟡 Médio | 🔵 Baixo (ajuste fino)*

---

## 7. Sugestões de Melhoria de UX/UI

### ⚡ Quick Wins (Ajustes Rápidos no Streamlit)
*Melhorias de alto impacto visual que podem ser aplicadas via CSS customizado (`st.markdown`) ou ajuste de microcopy:*
1. `[Ex.: Forçar cor de texto #293241 e border-radius: 10px nos botões primários via CSS]`
2. `[Ex.: Ajustar espaçamento interno (padding) dos cards e containers para reduzir sensação de aperto]`
3. `[Ex.: Melhorar microcopy da tela inicial para reforçar o conceito "Aprender com clareza, leveza e autonomia"]`

### ✨ Evoluções de UX (Pós-MVP)
*Ideias para elevar a experiência em versões futuras:*
1. `[Ex.: Criar indicador visual de progresso em 4 passos (stepper) fixo no topo da área central]`
2. `[Ex.: Adicionar alternância de modo de leitura / ajuste de tamanho de fonte para acessibilidade]`
3. `[Ex.: Migrar telas críticas para um frontend dedicado caso as limitações de layout do Streamlit restrinjam a evolução do Design System]`

---

## 8. Evidências Visuais

> Salve as capturas de tela em `docs/qa/evidencias/` (ex.: `desktop-home.png`, `mobile-home.png`, `ui-01-contraste.png`) e vincule abaixo:

* **Visão Geral (Desktop):** `![Desktop](./evidencias/desktop-home.png)`
* **Visão Geral (Mobile):** `![Mobile](./evidencias/mobile-home.png)`
* **Detalhe de Inconsistência:** `![Inconsistência](./evidencias/ui-01.png)`
