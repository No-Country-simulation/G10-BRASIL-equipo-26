# 👥 Equipe e Governança — MentorIA Tech (Equipe 26)

> Documento de referência oficial da equipe para o Hackathon ONE G10 (Oracle Next Education & Alura / NoCountry).  
> Atualizado em: 12/11/2026 — Responsável: Lídia Moura (Líder Técnica).

---

## 1. Composição da Equipe

Funções conforme cadastro oficial na NoCountry, com atuação real no projeto.

| Integrante | Função NoCountry | Atuação no projeto |
| :--- | :--- | :--- |
| **Lídia Moura** | BI Analyst | Liderança técnica, configuração OCI/IAM, QA, documentação e governança |
| **Andrea De Nardi Gonzalez** | Data Analyst | Compliance, Scrum Master e migração Trello → GitHub Projects |
| **Rodrigo Silva do Carmo** | Data Scientist | Arquitetura RAG/LLM, contratos Pydantic v2 e benchmark experimental |
| **Wagner Julio de Campos** | Full Stack Developer | Front-end Streamlit e integração de interface |
| **Josiane da Silva** | Full Stack Developer | Contribuições gerais de desenvolvimento full stack |
| **Marcos Vinicius Ferreira de Oliveira** | Backend Developer | Back-end, pipeline de ingestão e extração de documentos |
| **Lysara Jacó Pinheiro** | Data Analyst | Identidade de marca, Brandbook UX/UI v1.1 e marketing |
| **Vagner Marques de Souza Lopes** | Data Analyst | Dados, schemas e integração back-end |
| **Leonardo Santos** | Data Analyst | Dados e suporte à extração de documentos |
| **João Okuyama** | Data Analyst | Dados e administração inicial do GitHub |

---

## 2. Liderança e Decisões de Governança

### 2.1 Enquete de Liderança
Realizada no início do projeto via Discord.

| Candidata | Votos | Resultado |
|---|---|---|
| **Lídia Moura** | 7 / 7 | ✅ **Eleita — 100%** |

### 2.2 Enquete de Horário de Reunião
Realizada no início do projeto via Discord.

| Opção | Resultado |
|---|---|
| **Terça-feira às 19h30** | ✅ **Vencedora — 67%** |
| Outros horários | 33% |

### 2.3 Preferências de Área (Discord)
Levantamento de interesse de cada membro por área de atuação.

| Área | Interessados |
|---|---|
| Back-end / RAG / Agentes | Rodrigo, Marcos Vinicius, Wagner, Vagner, Leonardo, Josiane |
| OCI / DevOps / Infraestrutura | Lídia, Marcos Vinicius, Wagner |
| Produto / Dados / BI | Vagner, Leonardo, Lídia, Andrea, Rodrigo |
| QA / Documentação | Lídia, Marcos Vinicius, Andrea, Lysara |
| Front-end / UX | Wagner, Lysara, Josiane |

---

## 3. Grupos OCI — Compartimento `mentoria-tech`

Grupos criados no Oracle Cloud Infrastructure (IAM) para controle de acesso.

### `mentoria-tech-adm` — Administradores de infraestrutura OCI
Acesso completo ao compartimento `mentoria-tech`: buckets, policies, grupos e configurações.

| Membro |
|---|
| Lídia Moura |
| Andrea De Nardi Gonzalez |
| Lysara Jacó Pinheiro |
| Rodrigo Silva do Carmo |
| Vagner Marques de Souza Lopes |

### `mentoria-tech-dev` — Desenvolvimento
Acesso de leitura e escrita nos buckets `mentoria-tech-artifacts` e `mentoria-tech-documents`.

| Membro |
|---|
| Josiane da Silva |
| Leonardo Santos |
| Lídia Moura |
| Marcos Vinicius Ferreira de Oliveira |
| Rodrigo Silva do Carmo |
| Vagner Marques de Souza Lopes |
| Wagner Julio de Campos |

### `mentoria-tech-bi` — Dados e BI
Acesso de leitura às métricas e exportações em `mentoria-tech-observability`.

| Membro |
|---|
| João Okuyama |
| Josiane da Silva |
| Leonardo Santos |
| Lídia Moura |
| Lysara Jacó Pinheiro |
| Marcos Vinicius Ferreira de Oliveira |
| Rodrigo Silva do Carmo |
| Vagner Marques de Souza Lopes |
| Wagner Julio de Campos |

### `mentoria-tech-viewer` — Visualização restrita
Acesso somente leitura para acompanhamento geral.

| Membro |
|---|
| Andrea De Nardi Gonzalez |
| João Okuyama |
| Josiane da Silva |
| Leonardo Santos |
| Lídia Moura |
| Lysara Jacó Pinheiro |
| Rodrigo Silva do Carmo |
| Vagner Marques de Souza Lopes |
| Marcos Vinicius Ferreira de Oliveira |
| Wagner Julio de Campos |

---

## 4. Buckets OCI Configurados

| Bucket | Finalidade | Acesso |
|---|---|---|
| `mentoria-tech-artifacts` | JSONs de conteúdo educacional gerado | Dev + Adm |
| `mentoria-tech-documents` | Documentos técnicos enviados pelos usuários | Dev + Adm |
| `mentoria-tech-observability` | Métricas, logs e exportações BI (CSV) | BI + Adm |

Todos os buckets são do tipo **Standard**, visibilidade **Private**, na camada **Always Free**.

---

## 5. Ferramentas de Gestão

| Ferramenta | Uso |
|---|---|
| **GitHub Projects** | Kanban de tarefas (migrado do Trello) — responsável: Andrea |
| **Discord** | Comunicação principal e sprint meetings obrigatórias da equipe |
| **Google Meet** | Alternativa para compartilhamento de tela durante reuniões (usado em paralelo com o Discord, já que o compartilhamento de tela do Discord estava temporariamente desativado por questões legais da plataforma) |
| **Miro** | Mapeamento IPO e brainstorming visual — responsável: Lysara |
| **NoCountry** | Registro oficial de função e entregáveis |

---

## 6. Contribuições de Marca e Marketing

A identidade visual do projeto **MentorIA Tech** foi desenvolvida por **Lysara Jacó Pinheiro**, incluindo:

- **Brandbook UX/UI v1.1** — paleta de cores, tipografia, mascote e diretrizes de marca
- **Paleta de cores oficial:**
  - 🟢 Menta: `#A8E6CF`
  - 🟣 Lilás: `#CDB4DB`
  - 🌸 Rosa: `#FFC8DD`
  - ⬛ Grafite: `#293241`
- **Tipografia:** Inter (WCAG AA)
- **Mascote:** cérebro ilustrado
- **Miro — Mapa IPO:** [acessar board](https://miro.com/app/board/uXjVETxlMKY=/?share_link_id=20932850042)
- **Documentos salvos em:** `docs/assets-marca/` *(a ser populado pela Lysara)*

---

## 7. Transparência sobre uso de IA

A documentação, estrutura de testes e organização deste repositório contaram com apoio da ferramenta **Antigravity** (IA assistente) como instrumento de produtividade. Todo conteúdo foi gerado sob **supervisão, governança e revisão da Lídia Moura** (Líder Técnica). As decisões de produto, experimentos e validações foram conduzidos e aprovados pela Equipe 26.
