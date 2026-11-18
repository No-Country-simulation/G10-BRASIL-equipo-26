# 🎨 Guia de Design & UX/UI — MentorIA Tech

> **Projeto:** MentorIA Tech (Desafio NovaMente) | Hackathon ONE — Grupo 10 (Equipe 26)  
> **Conceito:** *Aprender com clareza, leveza e autonomia.*  
> **Referência completa:** [MentorIA-Tech_Brandbook_UXUI.pdf](./docs/design/MentorIA-Tech_Brandbook_UXUI.pdf) (Versão 1.1)

Este documento reúne os fundamentos visuais, diretrizes de experiência do usuário e tokens de interface para padronizar o desenvolvimento do MVP da **MentorIA Tech**.

---

## 1. Essência e Personalidade da Marca

A **MentorIA Tech** transforma documentação técnica em experiências de aprendizagem personalizadas.

* **Pilares:**
  * **Clara:** A informação deve ser fácil de localizar, entender e aplicar.
  * **Acolhedora:** Interface intuitiva, acessível e sem excesso de estímulos.
  * **Criativa:** Aprender pode ser envolvente, visual e interativo.
* **Personalidade:** Humana, Didática, Moderna e Confiável.

### Tom de Voz (UX Writing)
* **Simples**, sem infantilizar.
* **Didático**, sem excesso de jargão.
* **Encorajador**, sem exageros.
* **Objetivo** nas mensagens de erro e instruções.

---

## 2. Logotipo e Regras de Aplicação

O símbolo oficial conecta cognição, inteligência artificial e conhecimento estruturado:
* **Cérebro orgânico (Menta):** Humanização, cognição e aprendizado individual.
* **Rede neural e nós de IA (Lilás):** IA generativa, fluxo de dados e processamento RAG.
* **Livro estruturante (Rosa/Lilás):** Documentações técnicas e base sólida de conhecimento.

**Diretrizes de uso:**
* **Área de respiro:** Preservar margem mínima equivalente a `1M` ao redor do logotipo.
* **Fundo prioritário:** Utilizar preferencialmente sobre fundos claros (`#FFFFFF` ou `#FAFAFC`) para garantir contraste e legibilidade.
* **Integridade cromática:** Manter estritamente as cores originais dos nós e elementos do símbolo (arquivos disponíveis em `app/assets`).

---

## 3. Sistema de Cores

A paleta combina tons pastéis suaves para organização visual com tipografia escura para leitura confortável. **Priorize superfícies claras** e reserve as cores de destaque para ações, navegação e feedback.

### Paleta de Marca
| Cor | Hex | Função |
| :--- | :--- | :--- |
| **Verde Menta** | `#A8E6CF` | Principal (CTA primário, destaques principais) |
| **Lilás Pastel** | `#CDB4DB` | Secundária (ações secundárias, elementos de IA) |
| **Rosa Suave** | `#FFC8DD` | Destaque (accent, detalhes interativos) |
| **Verde Claro** | `#D8F3DC` | Superfícies suaves / feedback positivo |
| **Lavanda Clara** | `#EDE4F5` | Superfícies de apoio / badges |
| **Rosa Pálido** | `#FFF0F5` | Fundos leves de destaque |

### Cores Neutras
| Cor | Hex | Função |
| :--- | :--- | :--- |
| **Branco** | `#FFFFFF` | Cards e áreas de leitura |
| **Off-white** | `#FAFAFC` | Fundo geral da aplicação |
| **Cinza Suave** | `#F1F3F5` | Divisórias e estados neutros |
| **Grafite** | `#293241` | Textos principais e títulos |
| **Cinza Texto (Muted)** | `#657080` | Textos secundários, legendas e placeholders |

---

## 4. Tipografia

Preferir fontes *sans-serif* gratuitas e leves, como **`Inter`** ou **`system-ui`**, com fallbacks nativos do sistema operacional.

| Nível | Tamanho | Peso | Uso |
| :--- | :--- | :--- | :--- |
| **Título de página** | `28px – 32px` | Semibold (`600`) | Cabeçalhos principais de tela |
| **Subtítulo** | `18px – 22px` | Semibold (`600`) | Seções, títulos de cards e blocos |
| **Corpo de texto** | `14px – 16px` | Regular (`400`) | Conteúdo educacional, textos de apoio e formulários |

---

## 5. Experiência, Layout e Componentes

### Jornada de Criação (Fluxo Principal)
1. **Fontes:** Importar material base (`.pdf`, `.md` ou texto colado).
2. **Personalizar:** Definir perfil do destinatário e formato desejado.
3. **Gerar:** Processamento via IA + RAG com feedback visual de progresso.
4. **Aprender:** Revisar, estudar e exportar o objeto educacional gerado.

### Padrão de Layout
* **Estrutura:** Sidebar discreta + área central ampla de leitura/criação + painéis contextuais.
* **Estética:** Cards arredondados (`16px`), espaçamento regular, ícones simples e indicadores claros de progresso.

### Diretrizes de Componentes e Interação
* **Botões de Ação:** Usar verbos claros (ex.: *"Criar conteúdo"*, *"Minha biblioteca"*). Primário em **Verde Menta** (`#A8E6CF`) e secundário em **Lavanda/Lilás** (`#CDB4DB` / `#EDE4F5`), sempre com texto em **Grafite** (`#293241`).
* **Formulários:** Manter rótulos (*labels*) persistentes fora do campo (ex.: *"Perfil do destinatário"*).
* **Feedback:** Exibir mensagens textuais claras para estados de carregamento (*loading*), estado vazio (*empty state*), sucesso e erro.
* **Navegação:** Garantir foco visível ao navegar via teclado (`:focus-visible`).

---

## 6. Acessibilidade e Regras de Uso

* **Contraste (WCAG AA):** **Nunca** utilizar texto branco (`#FFFFFF`) sobre fundos menta, lilás ou rosa pastel. Utilizar sempre **Grafite** (`#293241`) para garantir legibilidade.
* **Independência de Cor:** Não depender apenas da cor para indicar sucesso, erro ou seleção — acompanhar sempre com texto explicativo ou ícone.
* **Responsividade:** Garantir boa experiência em *desktop* e *mobile*, preservando hierarquia de leitura e áreas clicáveis confortáveis.
* **Consistência:** Reutilizar os tokens abaixo em todos os módulos da aplicação.

---

## 7. Tokens para Desenvolvimento (Handoff)

### Variáveis CSS (`tokens.css`)
```css
:root {
  /* Cores de Marca */
  --color-primary: #A8E6CF;
  --color-secondary: #CDB4DB;
  --color-accent: #FFC8DD;
  --color-surface-mint: #D8F3DC;
  --color-surface-lavender: #EDE4F5;
  --color-surface-pink: #FFF0F5;

  /* Neutros e Superfícies */
  --color-bg: #FAFAFC;
  --color-surface: #FFFFFF;
  --color-border: #F1F3F5;
  --color-text: #293241;
  --color-text-muted: #657080;

  /* Bordas e Arredondamento */
  --radius-card: 16px;
  --radius-control: 10px;

  /* Tipografia */
  --font-family-base: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
```

### Sugestão de Tema para Streamlit (`.streamlit/config.toml`)
Caso a interface utilize Streamlit, os tokens base podem ser aplicados diretamente na configuração do tema:
```toml
[theme]
primaryColor = "#A8E6CF"
backgroundColor = "#FAFAFC"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#293241"
font = "sans serif"
```

---

## 8. Checklist de Handoff e Validação

- [ ] Tokens CSS / tema centralizados no projeto
- [ ] Componentes reutilizáveis padronizados
- [ ] Estados de vazio, erro e carregamento (*loading*) implementados
- [ ] Contraste WCAG AA (texto grafite em fundos pastéis) e navegação por teclado revisados
- [ ] Teste responsivo (desktop e mobile) concluído
- [ ] Integração real (Upload + IA/RAG + Exportação) validada
