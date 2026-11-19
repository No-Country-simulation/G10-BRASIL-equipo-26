# Roteiro Estratégico de Pitch (Demo Day 4m40s & Vídeo 2–3min) — MentorIA Tech

**Projeto:** MentorIA Tech — Equipe 26 | Hackathon ONE G10 (Oracle, Alura & NoCountry)  
**Formato Demo Day:** 4 min 40 s ao vivo *(margem de 20s antes do corte de 5 min)*  
**Formato Vídeo de Entrega:** 2 a 3 minutos em **Tema Claro** (tela cheia, sem barras de ferramentas ou abas extras)

---

## 1. Estrutura Narrativa em 5 Etapas (Storytelling "Trailer de Cinema")

### Etapa 1 — Problema / Gancho (~45s) · *Lídia Moura*
> *Não começar com "Somos o grupo X" nem com jargões técnicos.*

* **Pergunta provocativa (nós somos a própria persona):**  
  *"Em tempos de IA, tudo na tecnologia se atualiza em tempo recorde — durante este próprio Hackathon vimos modelos da API do Gemini mudarem e ferramentas como o GitHub Projects exigirem aprendizado constante para ontem. Quem aqui já abriu uma documentação densa ou a transcrição de uma aula e precisou dominar tudo rápido?"*
* **A dor real (vs. LLMs genéricas e NotebookLM):**  
  *"Jogar um documento gigante ou uma transcrição em uma LLM comum ou no NotebookLM até ajuda, mas obriga você a escrever prompts longos para dar contexto, saber exatamente o que perguntar e ainda correr o risco de alucinação sem rastreio de página."*

### Etapa 2 — Proposta de Valor / Solução (~35s) · *Lídia Moura*
* **Fórmula de valor:**  
  *"O **MentorIA Tech** traz um caminho mais leve, acessível e assertivo para estudantes (como os alunos do ONE e Alura) e profissionais de TI se manterem atualizados em menos de 1 minuto (com folga dentro da margem de 2 minutos) — sem perder tempo lendo textos densos ou virando especialista em prompts, sobrando tempo para o que realmente amam: construir tecnologia."*
* **Diferencial direto (Entradas, Saídas e Reuso):**  
  *"Em poucos cliques, você sobe um arquivo **`.pdf`, `.md` ou `.txt`** (como a transcrição de uma aula da Alura salva direto em `.txt`), escolhe seu perfil (`Iniciante`, `Jr/Pleno`, `Tech Lead` ou `Gestor`) e o formato (`Tutorial`, `Flashcards`, `Quiz`, `TL;DR`, `Roteiro` ou `Resumo`). Além disso, pode baixar tudo em **Markdown (`.md`), CSV (pronto para o Anki) e JSON** — conteúdo que inclusive pode ser reaproveitado em outras LLMs ou no NotebookLM."*

### Etapa 3 — Demonstração do MVP / Prova de Fogo (~1m45s) · *Vídeo Pré-Gravado (Tema Claro)*
> *Usar vídeo pré-gravado em tela cheia (Tema Claro) narrado ao vivo para evitar atrasos de carregamento ou falhas de rede.*

* **Documento sugerido na demo (conexão direta com finalistas do G10 + Método STAR):**  
  Usar o próprio documento de requisitos do projeto entregue pela NoCountry ou o guia do GitHub Projects (mostrando o contraste STAR: *Situação/Tarefa* de compreender dezenas de requisitos técnicos -> *Ação* no MentorIA Tech -> *Resultado* estruturado em segundos em vez de horas).
* **Fluxo enxuto (*happy path*, sem mostrar menus secundários):**
  1. **Upload / Seleção:** envio do documento em PT-BR e escolha do perfil + formato (`TL;DR` ou `Flashcards`) → mostrar que cada item gerado cita **a página e o trecho real** do documento.
  2. **Quiz Interativo (Diferencial Ativo):** gerar um `Quiz` para `Tech Lead` → mostrar que o gabarito **não aparece antes da hora**, iniciar rodada, mostrar o limite de **3 tentativas** com feedback na explicação fundamentada e os botões de exportação (**CSV para Anki**, **Markdown** e **JSON**).
  3. **Prova na Nuvem:** mostrar o status de envio confirmado do JSON estruturado para o bucket privado na **Oracle Cloud (`mentoria-tech-artifacts`)**.

### Etapa 4 — Arquitetura e Tecnologia Traduzida em Valor (~45s) · *Rodrigo Silva*
> *Traduzir escolhas técnicas em benefício para o usuário, sem listar frameworks soltos.*

* **Como foi construído (visão integrada de resultado — fala do Rodrigo):**
  * **Interface e API integradas:** os sistemas se comunicam automaticamente para que o usuário só precise enviar o arquivo uma vez (`.pdf`, `.md` ou `.txt`) e acompanhar o progresso em tempo real — com interface validada com **100% de acessibilidade e SEO no Lighthouse** e downloads prontos em **`.md`, `.csv` (Anki) e `.json`**.
  * **Benchmark RAG & Confiabilidade anti-alucinação:** *"Realizamos um benchmark de RAG utilizando cinco PDFs de diferentes tamanhos, com 40 configurações por documento (200 experimentos), para avaliar e selecionar os melhores parâmetros de recuperação."* Antes de exibir qualquer resposta, um validador automático (Pydantic v2) confere se as páginas e `chunk_ids` citados realmente existem no documento.  
    **Vantagem para o usuário:** garante que os trechos recuperados contenham informações suficientes, relevantes e rastreáveis para a geração dos materiais de estudo.
  * **Prompts adaptados + Auditoria por IA no Quiz:** *"Desenvolvemos prompts específicos para cada perfil e nível de conhecimento do usuário. Para o Quiz, implementamos uma auditoria por IA que avalia a dificuldade, a qualidade das questões e sua fidelidade ao documento, evitando alucinações."*  
    **Vantagem para o usuário:** recebe materiais didáticos de alta qualidade e 100% compatíveis com o documento enviado.
  * **Alta disponibilidade & Velocidade (`Groq -> Gemini`):** se o provedor principal de IA (**Groq `openai/gpt-oss-120b`**) oscilar ou atingir limite gratuito, o sistema alterna automaticamente para o provedor secundário (**Google Gemini**) com timeouts ajustados (`20s`/`30s`), reduzindo o Quiz completo de 5 questões para **`~13,7s`** sem interromper o estudo.
  * **Privacidade (LGPD) e Nuvem:** armazenamos o progresso com identificadores anônimos SHA-256 (zero coleta de nome, e-mail ou IP) e persistimos os artefatos na **Oracle Cloud (`mentoria-tech-artifacts`, Always Free)**.

### Etapa 5 — Impacto, Visão LATAM e Fechamento (~50s) · *Lídia Moura*
* **Impacto imediato:** *"Alunos do ONE podem subir até transcrições de aulas da Alura para revisar com Flashcards e Quizzes antes de aplicar no código."*
* **Visão LATAM & Evolução Estratégica (Roadmap Pós-MVP):**
  * **Base Trilíngue:** repositório e documentação de QA já estruturados em **Português, Espanhol e Inglês** para escalar na América Latina.
  * **Próximos Canais e Exportações:** evolução da nossa API pronta para **Extensão do Chrome** (estudar direto na aba da documentação sem trocar de tela), **Bot no Telegram** (que, diferente do WhatsApp, preserva arquivos sem perda de qualidade e oferece memória persistente em nuvem), **exportação direta em `.pdf`/`.txt`** (facilitando ainda mais o reuso no NotebookLM) e painel ativo no **Power BI** sobre a telemetria já coletada.
* **Fechamento:** *"MentorIA Tech: transformamos informação técnica complexa em aprendizado eficiente e confiável no ritmo de cada pessoa. Obrigado!"*

---

## 2. Checklist de Ouro da Live (Boas Práticas & Erros a Evitar)

### O que DEVE acontecer
- [ ] Ensaiar em voz alta com cronômetro **pelo menos 5 vezes** (meta: **4m40s**, máximo 5m).
- [ ] Manter **Tema Claro (Light)** do Streamlit no vídeo e nas telas.
- [ ] Vídeo gravado em **tela cheia**, sem barra de favoritos/abas extras.
- [ ] Slides no Canva enxutos (pouco texto, tópicos visuais).
- [ ] No Q&A: ouvir até o fim, respirar **3 segundos** antes de responder, papéis definidos (sem falar por cima) e posicionar itens futuros no *roadmap* com segurança.

### O que NÃO PODE acontecer
- [ ] Ultrapassar **5 minutos** (microfone é cortado).
- [ ] Abrir com *"Somos o grupo X"* ou jargão técnico antes da dor real.
- [ ] Ler slides ou tentar mostrar todas as telas/botões secundários.
- [ ] Pedir desculpas pelo que não foi incluído ou inventar respostas no Q&A.
- [ ] Exibir chaves, `.env` ou dados pessoais na gravação.

---

## 3. Sugestões Práticas para os Slides no Canva (`MentorIA-Tech_Pitch_Hackathon.pptx`)

> Revisão realizada sobre os 8 slides atuais sem editar o arquivo original no Canva:

1. **Slide 1 (Capa):**
   * Corrigir a caixa de texto do link do GitHub que está quebrada ao meio (`G10-BRASIL-e` / `quipo-26`).
   * Manter visual limpo com o título **MentorIA Tech** e o slogan oficial: *"Aprender com clareza, leveza e autonomia."*
2. **Slide 2 (Contexto / Problema & Solução):**
   * Conectar diretamente o problema à dor da persona (ter que aprender ferramentas novas como GitHub Projects ou documentações densas para ontem, sem saber qual prompt escrever).
   * Destacar os **3 cliques** (Documento + Perfil + Formato) e os **benefícios imediatos**: economia de semanas para menos de 1 minuto, zero alucinação com citação de páginas e exportação pronta (Anki CSV, Markdown, JSON).
3. **Slide 3 (Arquitetura — ATENÇÃO CRÍTICA):**
   * **Substituir a tabela genérica** (`Modelo A / Modelo B / Modelo Escolhido / 450 ms / 94%`) — esses números são de template fictício e não devem ser sustentados diante da banca.
   * Trocar pelos **fatos reais validados**:
     * **Benchmark RAG & Auditoria:** `200 experimentos` (`5` PDFs × `40` configs) → `chunk_size=2000`, `overlap=200`, `K=10`, `top_n=5`, prompts por perfil/nível + auditoria por IA no Quiz.
     * **Resiliência, Latência & QA:** Multi-LLM (**Groq** principal + **Google Gemini** fallback, Quiz de 5 questões em **`13,7s`**) + validação **Pydantic v2** + entradas `.pdf/.md/.txt` e downloads `.md/.csv/.json` + **OCI Always Free** (`mentoria-tech-artifacts`) + **Zero PII (LGPD)**.
4. **Slide 4 / 5 (MVP em Ação — Vídeo):**
   * Inserir o vídeo gravado em **Tema Claro (tela cheia, 60–90s)** mostrando o fluxo principal: documento → perfil/formato com fontes → Quiz interativo (3 tentativas sem gabarito antecipado) → confirmação do upload OCI.
5. **Slide 6 (Equipe 26 + Fechamento):**
   * Ajustar o texto solto `Tech Lead` para junto de **Lídia Moura** (`Lídia Moura — Tech Lead · OCI, QA & Documentação`).
   * Corrigir o typo `AI Enginner` → `AI Engineer` no card de Rodrigo do Carmo.
   * Recomenda-se incluir (antes ou junto do encerramento) 3 tópicos visuais de **Benefícios & Visão LATAM (Pós-MVP)**: documentação trilíngue (`PT-BR / ES / EN`), evolução para **Extensão do Chrome** + **Bot no Telegram** (persistência em nuvem sem perda de qualidade) e painel ativo no **Power BI**.
6. **Slides 7 e 8 (Páginas de Identidade Visual / Brandbook — criado pela Lys):**
   * **Manter 1 slide/card focado na identidade visual do MVP (criada pela Lys):** ela reforça diretamente a nossa proposta de trazer um caminho mais leve, acessível e didático para estudantes e profissionais de tecnologia aprenderem no seu ritmo — garantindo apenas que não haja menção ao termo antigo `nicho` (já descontinuado). Ocultar apenas slides excedentes de paleta/regras técnicas para não quebrar o ritmo após o fechamento.

