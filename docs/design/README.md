# 🎨 Documentação de Design (UX/UI) — MentorIA Tech

> **Projeto:** MentorIA Tech *(Desafio NovaMente — Hackathon ONE / Grupo 10)*  
> **Conceito:** Aprender com clareza, leveza e autonomia.

Esta pasta reúne toda a documentação de **Product Discovery, Arquitetura de Informação, Identidade Visual, Wireframes, Prototipação e Validação** do **MentorIA Tech** — uma plataforma EdTech baseada em IA e RAG que transforma documentações técnicas densas em trilhas de estudo ativo (*Flashcards*, *Quizzes*, *Passo a Passo* e *Resumos*) para estudantes e profissionais de tecnologia do programa **ONE (Oracle Next Education)**.

---

## 🗂️ Estrutura e Índice de Artefatos

Os documentos estão organizados seguindo a cronologia do processo de design (*Double Diamond*):

| Etapa | Artefato | Descrição |
| :--- | :--- | :--- |
| **01. Estratégia** | [`01-discovery-e-estrategia-produto.md`](./docs/design/01-discovery-e-estrategia-produto.md) | Contexto do mercado EdTech no Brasil, Matriz CSD, Benchmarking competitivo, Proposta de Valor Única (UVP) e priorização de MVP (MoSCoW). |
| **02. Empatia** | [`02-persona-e-jornada-usuario.md`](./02-persona-e-jornada-usuario.md) | Definição da Proto-Persona (estudante/profissional em transição no programa ONE) e Mapa da Jornada do Usuário ponta a ponta. |
| **03. Estrutura** | [`03-arquitetura-informacao-e-user-flow.md`](./03-arquitetura-informacao-e-user-flow.md) | Sitemap, especificação funcional dos 4 módulos principais (*Home*, *Biblioteca de Fontes*, *Estúdio de Criação* e *Biblioteca de Conteúdo*) e *User Flow*. |
| **04. Ideação UI** | [`04-wireframes-e-prompts-stitch.md`](./04-wireframes-e-prompts-stitch.md) | Diretrizes estruturais de layout (*Split-View*), prompts utilizados no Google Stitch e referência visual dos wireframes de baixa fidelidade (`/wireframes`). |
| **05. Identidade** | [`05-design-system-e-tokens.md`](./05-design-system-e-tokens.md) | Tokens CSS de cor, tipografia, bordas, regras de contraste WCAG AA e suporte a blocos de código. Complementado pelo [`mentoria-tech-brandbook-v1.1.pdf`](./mentoria-tech-brandbook-v1.1.pdf). |
| **06. Validação** | [`06-validacao-prototipo-e-dogfooding.md`](./06-validacao-prototipo-e-dogfooding.md) | Registro dos testes de usabilidade internos (*Dogfooding* com a equipe do Hackathon), ajustes aplicados no MVP e roteiro para validação externa. |
| **Protótipo** | [`prototipo/index.html`](./prototipo/index.html) | Protótipo navegável interativo em arquivo único (HTML/CSS/JS) com persistência local para simulação do fluxo completo. |

---

## 📁 Árvore de Arquivos da Pasta `design/`

```text
design/
├── README.md                                     
├── 01-discovery-e-estrategia-produto.md          
├── 02-persona-e-jornada-usuario.md               
├── 03-arquitetura-informacao-e-user-flow.md      
├── 04-wireframes-e-prompts-stitch.md             
├── 05-design-system-e-tokens.md                  
├── 06-validacao-prototipo-e-dogfooding.md            
├── mentoria-tech-brandbook-v1.1.pdf              
├── wireframes/                                   
│   ├── 04.1-wireframe-home-dashboard.png
│   ├── 04.2-wireframe-biblioteca-fontes.png
│   ├── 04.3-wireframe-estudio-criacao.png
│   └── 04.4-wireframe-biblioteca-conteudo.png
├── prototipo/                                    
│   └── index.html
└── qa/                                           
    ├── relatorio_de_qa_de_ux_ui_streamlit.md
    └── evidencias/                               
```

---

## 🔗 Acesso Rápido ao Protótipo Navegável

* **Execução Local:** Basta abrir o arquivo [`design/prototipo/index.html`](./prototipo/index.html) diretamente em qualquer navegador moderno (não requer servidor ou dependências externas).
