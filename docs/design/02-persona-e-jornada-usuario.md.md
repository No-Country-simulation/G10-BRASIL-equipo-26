# Proto-Persona e Mapa da Jornada do Usuário — MentorIA Tech

* **Etapa de Design:** UX Research & Definição (Empatia e Mapeamento de Experiência)
* **Relação com Arquitetura:** Alinhado à estrutura de navegação em 4 pilares (*Home*, *Biblioteca de Fontes*, *Estúdio de Criação*, *Biblioteca de Conteúdo*).

---

## 1. Proto-Persona

### Lucas Andrade, 26 anos
* **Perfil:** Estudante da trilha de Back-end (Java / Spring Boot / OCI) no programa **ONE — Oracle Next Education** e auxiliar administrativo em transição de carreira.
* **Localização & Rotina:** Região Metropolitana de São Paulo. Trabalha 8h por dia e estuda à noite (21h às 23h30) e aos sábados. Consome revisões rápidas pelo celular no transporte público.
* **Nível Técnico:** Intermediário em lógica de programação; iniciante em infraestrutura de nuvem e leitura de documentações oficiais extensas.

#### Objetivos e Motivações
* Concluir os *Challenges* do programa ONE dentro do prazo com código limpo e funcional.
* Construir portfólio sólido no GitHub e conquistar a primeira vaga como Desenvolvedor Júnior.
* Aprender a consultar documentações oficiais sem depender apenas de tutoriais em vídeo desatualizados.

#### Dores e Frustrações
* **Sobrecarga Cognitiva:** Documentações técnicas (ex.: Spring Security, Oracle Cloud Infrastructure) são densas, extensas e muitas vezes em inglês técnico complexo.
* **Estudo Passivo e Baixa Retenção:** Lê páginas inteiras da documentação e sente que esqueceu os comandos principais no dia seguinte.
* **Atrito com IAs Genéricas:** Perde muito tempo copiando trechos para o ChatGPT, ajustando prompts e formatando manualmente anotações e cartões de revisão.
* **Falta de Organização:** Arquivos PDF, resumos e testes ficam espalhados entre pastas locais, Notion e abas perdidas do navegador.

> *"Eu não tenho 3 horas livres para ler 80 páginas de documentação antes de começar a codar o Challenge. Preciso extrair o passo a passo prático rápido e ter um jeito fácil de revisar os comandos no celular depois."*

---

## 2. Mapa da Jornada do Usuário (User Journey Map)

**Cenário:** Lucas precisa implementar autenticação JWT em uma API Spring Boot para entregar um *Challenge* do ONE até sexta-feira. Ele baixou o guia oficial em PDF e vai usar o **MentorIA Tech** pela primeira vez.

| Etapa da Jornada | **1. Descoberta & Início** *(Home)* | **2. Ingestão do Material** *(Biblioteca de Fontes)* | **3. Parametrização & Geração** *(Estúdio de Criação)* | **4. Consolidação & Estudo Ativo** *(Biblioteca de Conteúdo)* |
| :--- | :--- | :--- | :--- | :--- |
| **Ações do Usuário** | Acessa a plataforma, visualiza o painel geral com as descrições gerais da plataforma e inicia um novo ciclo de estudo. | Faz upload do PDF técnico (`spring-security-jwt.pdf`), adiciona tags (`Java`, `Spring`, `Challenge-03`) e valida o status de indexação RAG. | Seleciona a fonte recém-carregada, escolhe os formatos desejados (*Passo a Passo*, *Flashcards* e *Quiz*), ajusta o nível de profundidade e pré-visualiza o resultado antes de salvar. | Acessa o pacote gerado na Biblioteca de Conteúdo, segue o passo a passo para codar e usa o celular no dia seguinte para responder ao Quiz e revisar os Flashcards. |
| **Pensamentos** | *"Preciso organizar o que estou estudando para esse Challenge sem me perder em várias abas."* | *"Ótimo, meu PDF técnico já está catalogado aqui e não vou precisar ficar subindo o arquivo toda vez."* | *"Quero focar na implementação prática primeiro. Deixa eu conferir na pré-visualização se os blocos de código vieram inteiros."* | *"Agora tenho o guia prático aberto ao lado da minha IDE e os flashcards prontos para revisar no ônibus."* |
| **Emoções** | Determinado, mas pressionado pelo prazo. | Aliviado pela centralização dos arquivos. | Engajado e no controle (sensação de personalização sem esforço de prompt). | Confiante e produtivo; percebe evolução real no aprendizado. |
| **Pontos de Atrito (Riscos UX)** | Tela inicial confusa ou sem chamada clara para iniciar uma nova capacitação. | Demora no processamento de PDFs grandes sem feedback visual claro do progresso. | Geração demorada sem indicador de etapa ou pré-visualização que quebra a formatação do código. | Dificuldade para filtrar conteúdos por tecnologia/tag ou experiência ruim de leitura de código no mobile. |
| **Oportunidades de Design** | Exibir progresso visual das trilhas ativas e atalho rápido *"Novo Estudo a partir de Fonte"*. | Exibir metadados úteis (nº de páginas, status RAG pronto, preview rápido da fonte). | Permitir regenerar apenas uma seção específica na pré-visualização antes de exportar para a Biblioteca de Conteúdo. | Disponibilizar botão de *"Copiar Código"* em 1 clique no Passo a Passo e modo foco/mobile nos Flashcards e Quizzes. |
