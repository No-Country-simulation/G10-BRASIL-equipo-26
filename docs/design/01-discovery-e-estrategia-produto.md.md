# Product Discovery & Estratégia de UX — MentorIA Tech

* **Etapa de Design:** UX Strategy / Product Discovery (Imersão & Definição)
* **Público-Alvo (Persona):** Estudantes e profissionais de tecnologia integrantes do programa **ONE — Oracle Next Education**
* **Objetivo do Documento:** Consolidar o entendimento de mercado, alinhar hipóteses (Matriz CSD), mapear concorrentes (Benchmarking) e definir a Proposta de Valor Única (UVP) e o escopo funcional do MVP.

---

## 1. Contexto de Mercado (EdTech Brasil)

O ecossistema brasileiro de tecnologia educacional concentra a maior fatia da América Latina e atravessa uma fase de maturidade orientada à **eficácia pedagógica mensurável**, **empregabilidade** e **retenção**.

### Fatores-Chave que Impactam o Produto
* **Acesso Mobile-First e Microlearning:** Estudantes possuem rotinas fragmentadas e sofrem com sobrecarga cognitiva em conteúdos longos; formatos curtos e acionáveis aumentam a taxa de conclusão.
* **Comoditização da IA Genérica:** Ferramentas gratuitas de IA generativa já fazem parte do cotidiano dos estudantes de tecnologia, exigindo que novas EdTechs entreguem **fluxos pedagógicos estruturados** em vez de apenas interfaces de chat abertas.
* **Foco em Aplicação Prática:** No segmento de capacitação técnica (*upskilling/reskilling*), o valor percebido está diretamente ligado à capacidade de aplicar o conhecimento em desafios reais (*challenges*), projetos e entrevistas.

---

## 2. Matriz CSD (Certezas, Suposições e Dúvidas)

Ferramenta de alinhamento utilizada para mapear o nível de conhecimento atual sobre o problema e orientar os experimentos de validação do MVP.

| **Certezas** *(Dados consolidados)* | **Suposições** *(Hipóteses a validar no MVP)* | **Dúvidas** *(Pontos de investigação com usuários)* |
| :--- | :--- | :--- |
| **Perfil da Persona:** Alunos do programa ONE têm alta carga de estudo prático e precisam consultar documentações técnicas densas em inglês/português. | **Estudo Ativo vs. Passivo:** Transformar docs em *quizzes* e *flashcards* aumenta a retenção de conteúdo técnico em comparação à leitura passiva ou resumos simples. | **Barreira frente às IAs gratuitas:** O que faz um aluno preferir o MentorIA Tech ao invés de usar prompts manuais no ChatGPT ou subir o PDF no Google NotebookLM? |
| **Mobile-First e Microlearning:** Sessões curtas de revisão (5–10 min) têm maior aderência na rotina corrida de quem concilia trabalho e estudos. | **Zero Atrito Operacional:** Eliminar a necessidade de engenharia de prompt e geração manual de cartões economiza tempo crítico durante entregas de *challenges*. | **Formato de Maior Valor:** Entre *Resumo*, *Passo a Passo*, *Flashcards* e *Quiz*, qual recurso gera o "momento Aha!" imediato no primeiro uso? |
| **Rigor Técnico:** Documentações de TI exigem preservação exata de sintaxe, blocos de código e comandos. | **Roteiro Hands-on:** Gerar um passo a passo prático a partir da documentação acelera o *setup* e a resolução de problemas técnicos. | **Retenção e Recorrência:** Com que frequência o aluno volta à plataforma após concluir o estudo de um documento específico? |

---

## 3. Benchmarking Competitivo

Análise comparativa considerando soluções de grandes empresas, startups especializadas e fluxos manuais adotados por estudantes autônomos.

| Categoria | Player | Abordagem / Solução | Vantagens para a Persona (ONE) | Desvantagens / Lacunas (*Gaps*) |
| :--- | :--- | :--- | :--- | :--- |
| **Big Tech** *(IA Nativa)* | **Google NotebookLM** | Upload de PDFs e links para gerar resumos, guias de estudo e podcasts em áudio baseados nas fontes. | Gratuito, excelente precisão de RAG (citação de fontes) e suporte a arquivos extensos. | **Experiência passiva:** foca em leitura e áudio; não oferece *quizzes* interativos nem treino de memorização ativa. |
| **Big Tech** *(Produtividade)* | **Notion + Notion AI** | Workspace de anotações com assistente de IA para resumir páginas e organizar tarefas. | Já faz parte do fluxo de organização de muitos estudantes do ecossistema tech. | Custo adicional em dólar e ausência de estrutura pedagógica ativa (sem *flashcards* nativos ou testes de validação). |
| **Startup / EdTech** *(Estudo Ativo)* | **Quizlet** | Conversão de notas e documentos em *flashcards*, testes práticos e jogos de memorização. | Forte apelo de memorização ativa e experiência *mobile-first* otimizada para revisão rápida. | Genérico; pouco adaptado para preservar blocos de código e gerar **passo a passo técnico de implementação**. |
| **Startup / SaaS** *(Chat com PDF)* | **ChatPDF / Humata AI** | Interface conversacional dedicada a tirar dúvidas pontuais sobre arquivos PDF enviados. | Curva de aprendizado zero; rápido para consultas pontuais em manuais. | **Zero jornada pedagógica:** depende da qualidade das perguntas do usuário e não estrutura trilhas de aprendizado. |
| **Fluxo Autônomo** *(DIY)* | **ChatGPT (Free) + Anki** | Extração manual de resumos no ChatGPT e criação manual de baralhos no Anki. | Custo zero e controle total sobre o material de revisão espaçada. | **Alto atrito operacional:** exige engenharia de prompt constante e trabalho manual repetitivo de copiar/colar. |

### Oportunidades Identificadas (Diferenciais Competitivos)
1. **Ciclo Ativo Completo:** Unir compreensão teórica, execução prática e validação de aprendizado em um único fluxo contínuo.
2. **RAG Especializado em Código:** Pipeline de processamento que preserva indentação, comandos, trechos de código e arquitetura sem "achatar" o conteúdo técnico.
3. **Automação Pedagógica em 1 Clique:** Entrega imediata de estrutura de estudo sem exigir engenharia de prompt do estudante.

---

## 4. Proposta de Valor Única (UVP)

> **Para estudantes e profissionais de tecnologia do programa ONE** que precisam dominar documentações técnicas densas em pouco tempo, o **MentorIA Tech** é uma **plataforma de estudo ativo guiado por IA** que transforma qualquer documentação técnica em trilhas práticas de **passo a passo, flashcards e quizzes interativos com código preservado** — eliminando a passividade dos leitores de PDF e o trabalho manual de criar prompts e cartões de revisão.

---

## 5. Priorização de Escopo do MVP (Matriz MoSCoW)

Definição dos requisitos funcionais para a primeira versão testável do produto, orientando as próximas etapas de **Arquitetura de Informação**, **User Flow** e **Prototipação de UI**.

### Must Have *(Essenciais para validar a UVP na V1)*
* **Ingestão de Documentação Técnica:** Upload de arquivos (`PDF`, `MD`, `TXT`) com *chunking* inteligente que preserva blocos de código e hierarquia de títulos.
* **Resumo Executivo Estruturado:** Síntese dos conceitos-chave, pré-requisitos e casos de uso com referência aos trechos originais do documento.
* **Gerador de Passo a Passo Prático (*Hands-on*):** Conversão da documentação em um roteiro sequencial acionável (*Setup $\rightarrow$ Configuração $\rightarrow$ Execução $\rightarrow$ Validação*).
* **Flashcards Técnicos Automáticos:** Pares Frente/Verso focados em comandos, conceitos, comparações e *troubleshooting*.
* **Quiz Interativo com Feedback:** Questões de múltipla escolha (incluindo análise de código/cenários) com explicação fundamentada no documento enviado.

### Should Have *(Importantes — Próxima iteração pós-validação)*
* **Exportação de Materiais:** Download dos flashcards para Anki (`.csv`/`.apkg`) e do resumo/passo a passo em Markdown (`.md`).
* **Chat Contextualizado ("Tire Dúvidas"):** Assistente lateral restrito ao escopo do documento enviado para dúvidas pontuais durante a prática.
* **Histórico de Documentos:** Persistência dos materiais processados para retomada de estudo.

### Could Have *(Desejáveis — V2)*
* **Repetição Espaçada (SRS) Nativa:** Agendamento inteligente de revisão baseado nos erros cometidos no quiz.
* **Ingestão via URL:** Extração direta a partir de links de documentações oficiais (ex.: OCI, Oracle Java, Spring, Python).
* **Desafios de Código (*Fill-in-the-blank*):** Exercícios práticos de preenchimento de comandos ou trechos de código.

### Won't Have *(Fora do escopo atual)*
* Geração de podcasts em áudio (alto custo computacional e já coberto por players gratuitos como NotebookLM).
* Gamificação complexa (rankings globais, avatares, lojas virtuais).
* Indexação de múltiplos repositórios inteiros do GitHub ou vídeos longos na V1.

---

## 6. Fluxo Mínimo do Usuário (User Flow V1)

```text
[Tela Inicial / Upload]
       │
       ▼ (Upload de PDF / MD / TXT técnico)
[Processamento RAG & Indexação]
       │
       ▼ (Geração automática em 1 clique)
[Workspace de Estudo — Navegação em 4 Abas]
       ├──► Aba 1: Resumo Estruturado (Visão Geral)
       ├──► Aba 2: Passo a Passo Prático (Hands-on)
       ├──► Aba 3: Flashcards Técnicos (Memorização)
       └──► Aba 4: Quiz Interativo (Validação com Feedback)
```

---

## 7. Próximos Passos de UX/UI
- [ ] **Proto-Persona & Jornada do Usuário:** Detalhar o cenário de uso de um aluno do ONE estudando uma documentação para um *Challenge*.
- [ ] **Arquitetura de Informação & Wireframes (Baixa Fidelidade):** Desenhar o layout do fluxo de upload e da visualização das 4 abas de estudo (foco em legibilidade de blocos de código e responsividade).
- [ ] **Teste de Conceito / Usabilidade:** Validar o protótipo e o MVP funcional com 5 a 8 colegas da turma do ONE para mover itens da coluna *Suposições* para *Certezas* na Matriz CSD.