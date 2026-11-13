# Engenharia de Prompts Estratégica, Eficiência de Tokens e Inteligência de Mercado — MentorIA Tech

**Responsável:** Lídia Moura (Lidi) — Líder Técnica (com contribuições de Rodrigo Silva e Equipe 26)  
**Data da última atualização:** 09/11/2026  
**Status:** Framework Oficial de Engenharia de Prompts e Posicionamento Competitivo do MVP

---

## 1. Frameworks Estratégicos de Engenharia de Prompts (Máximo Resultado com Mínimo Consumo de Tokens)

Para obter respostas pedagógicas ricas sem desperdiçar a janela de contexto e a cota gratuita de tokens (*Rate Limit*), o **MentorIA Tech** combina **4 frameworks clássicos de Prompt Engineering** adaptados para saída estruturada (JSON Schema):

### 1.1. Matriz de Frameworks por Dimensão
| Framework | Como aplicamos no MentorIA Tech | Economia de Tokens & Ganho de Qualidade |
| :--- | :--- | :--- |
| **CO-STAR Compacto** *(Context, Objective, Style, Tone, Audience, Response)* | Estrutura o cabeçalho da requisição em blocos curtos e determinísticos (`Perfil`, `Formato`, `Nicho`, `Nível`), eliminando instruções prolixas ou redundantes. | Reduz em ~35% o tamanho do *System Prompt* mantendo direção pedagógica cirúrgica. |
| **Role-Goal-Constraints (RGC) + Anti-Injection** | Define o papel exato do especialista instrucional, o objetivo por formato e a restrição férrea de usar **exclusivamente** os `[CHUNK id=... paginas=...]` fornecidos. | Impede alucinações fora do documento e bloqueia *Prompt Injection* vindo do PDF. |
| **Schema-Driven Generation (Zero-Prose JSON)** | Utiliza `response_mime_type="application/json"` (Gemini) e `response_format={"type": "json_object"}` (Groq) acoplado ao JSON Schema do Pydantic v2, proibindo texto conversacional (`"Aqui está seu resumo..."`) e raciocínio aberto (*Chain-of-Thought* longo). | Economiza até **40% de tokens de saída (output tokens)**, que são os mais caros e lentos nas APIs de LLM. |
| **Micro-Templates por Perfil × Formato × Nicho** | Em vez de enviar vários exemplos longos (*Few-Shot* pesado), injeta uma **Diretriz Pedagógica de 2 linhas** específica para a combinação escolhida pelo usuário. | Preserva a janela de 28.000 caracteres quase inteiramente para os trechos reais do documento. |

---

## 2. Diretrizes de Adaptação por Perfil (Personas Atualizadas)

Conforme alinhamento técnico (Rodrigo Silva & Lídia Moura), os 4 perfis operam com recortes cognitivos distintos sobre o mesmo documento técnico:

| Perfil | Tom, Vocabulário e Foco Cognitivo no Prompt | Tratamento de Exceção de Escopo |
| :--- | :--- | :--- |
| **1. `Iniciante` (Transição de Carreira)** | **Tom:** Acolhedor, claro e didático. **Regra:** Explicar siglas e jargões na primeira ocorrência usando analogias concretas do cotidiano antes da definição formal. Focar nos conceitos fundacionais ("o que é" e "para que serve"). | Sempre aplicável a qualquer documento técnico. |
| **2. `Jr/Pleno` (Desenvolvedor)** | **Tom:** Prático e mão na massa (*hands-on*). **Regra:** Focar em implementação, configuração, parâmetros, fluxo de execução, erros comuns e aplicação direta no código/infraestrutura. | Sempre aplicável a manuais e guias técnicos. |
| **3. `Tech Lead` *(anteriormente Arquiteto)*** | **Tom:** Analítico, sistêmico e crítico. **Regra:** Focar em decisões arquiteturais, trade-offs, segurança, limites operacionais, escalabilidade, resiliência e governança técnica. | Aplicável a documentações técnicas e de arquitetura. |
| **4. `Executivo` *(anteriormente Gestor)*** | **Tom:** Objetivo, estratégico e orientado a valor/risco. **Regra:** Traduzir componentes técnicos em impacto de negócio, eficiência operacional, segurança corporativa, custos e tomada de decisão. | **Regra Crítica:** Se o documento for 100% operacional/matemático e não permitir extração executiva fiel sem inventar dados, retornar `{"erro": "perfil_sem_contexto"}` e exibir aviso amigável ao usuário sugerindo os perfis `Tech Lead` ou `Jr/Pleno`. |

---

## 3. Diretrizes de Adaptação por Formato Pedagógico (6 Saídas)

1. **`Tutorial` (Guia Passo a Passo):**
   * *Regra de Prompt:* Ordenar os conceitos em sequência lógica de execução (`Passo 1 -> Passo N`), onde cada passo contém uma ação clara no `titulo` e o "como/por que fazer" na `explicacao`, citando o `chunk_id` exato.
2. **`Flashcards` (Memorização Ativa / Anki):**
   * *Regra de Prompt:* Aplicar o **Princípio da Informação Mínima** (SuperMemo/Anki): cada `pergunta` deve cobrar **um único conceito atômico** e cada `resposta` deve ser direta, objetiva e autoexplicativa (ideal para revisão espaçada).
3. **`Quiz` (Avaliação com Justificativa e Distratores Plausíveis):**
   * *Regra de Prompt:* Criar `enunciado` contextualizado no `Nicho` escolhido; elaborar 4 `alternativas` de tamanho semelhante onde os distratores (opções incorretas) representem confusões conceituais reais (e não opções absurdas), acompanhadas de `explicacao` pedagógica fundamentada na página original.
4. **`TL;DR` (Síntese Executiva Rápida):**
   * *Regra de Prompt:* Resumo denso de 1 parágrafo com a tese central do documento + lista de `pontos_chave` acionáveis em *bullet points* curtos.
5. **`Roteiro` (Sequência de Aula / Estudo Guiado):**
   * *Regra de Prompt:* Dividir o estudo em `etapas` progressivas (Introdução Conceitual -> Aprofundamento -> Prática/Fixação) com estimativa realista de `duracao_minutos` para cada bloco.
6. **`Resumo` (Síntese Estruturada por Seções):**
   * *Regra de Prompt:* Organizar os capítulos/temas do documento em `secoes` temáticas com `titulo` e `texto` coeso, servindo como apostila de revisão completa.

---

## 4. Contextualização por Nicho (`Geral`, `Fintech`, `Saúde`, `E-commerce`)

> **Regra de Ouro Anti-Alucinação no Nicho:**  
> O `Nicho` **nunca** deve alterar os fatos técnicos do documento original. Ele atua exclusivamente como **lente de exemplificação**:
* **`Fintech`:** exemplifica segurança, latência ou modelos preditivos sob a ótica de transações financeiras, prevenção a fraude e conformidade bancária.
* **`Saúde`:** exemplifica proteção de dados (LGPD/dados sensíveis de pacientes), disponibilidade crítica e triagem clínica.
* **`E-commerce`:** exemplifica picos de tráfego (Black Friday), recomendação de produtos, catálogo e conversão.
* **`Geral`:** mantém os exemplos originais nativos do próprio documento técnico.

---

## 5. Análise Crítica de Mercado: Concorrentes vs. Diferencial do MentorIA Tech

Para posicionar o **MentorIA Tech** perante a banca avaliadora (Demo Day) e o mercado de **EdTech & Corporate L&D (Treinamento Corporativo)**, mapeamos os principais concorrentes diretos e indiretos:

### 5.1. Matriz Comparativa de Mercado

| Critério / Capacidade | **Google NotebookLM** | **ChatGPT / Claude (Uso Direto)** | **Quizlet AI / Revisely / Mindgrasp** | **🌸 MentorIA Tech (Nosso MVP)** |
| :--- | :--- | :--- | :--- | :--- |
| **Ancoragem em Fonte Real (RAG com Citação de Página/Chunk)** | ✅ Forte (cita trechos no chat) | ⚠️ Frágil (pode misturar conhecimento externo sem avisar) | ❌ Baixa (geralmente não valida página por item) | ✅ **Rigorosa e Determinística** (Pydantic rejeita o pacote se o `chunk_id` ou página não existir) |
| **Adaptação Explícita por Senioridade (`Iniciante` vs `Jr/Pleno` vs `Tech Lead` vs `Executivo`)** | ❌ Não nativa (exige engenharia de prompt manual do usuário a cada pergunta) | ⚠️ Manual (depende da habilidade do usuário em escrever prompts) | ❌ Foco genérico escolar/universitário | ✅ **Nativa em 1 clique** (parametrizada por Persona e Nível de Profundidade) |
| **Contextualização por Setor (`Fintech`, `Saúde`, `E-commerce`)** | ❌ Não possui | ⚠️ Manual | ❌ Não possui | ✅ **Nativa** (adapta analogias e casos de uso ao setor da empresa/aluno) |
| **Saída JSON Estritamente Tipada (Pronta para API / Integração LMS / Anki CSV)** | ❌ Fechado (não exporta contrato JSON validado para sistemas externos) | ⚠️ Exige desenvolvimento via API | ⚠️ Exportação limitada a cartões simples | ✅ **6 Contratos Pydantic v2 + Exportação JSON, Markdown e CSV (Anki)** |
| **Resiliência Multi-Provedor (Failover Automático + Pool de Chaves)** | 🔒 Preso a um único fornecedor | 🔒 Preso a um único fornecedor | 🔒 Caixa-preta proprietária | ✅ **Arquitetura Agnóstica Resiliente** (Gemini Principal -> Fallback Groq + Pool de chaves) |
| **Governança Corporativa & Privacidade (OCI Privada + Zero PII)** | ⚠️ Nuvem pública de consumo | ⚠️ Exige licenças Enterprise caras | ❌ SaaS voltado ao consumidor final | ✅ **OCI Object Storage Privado + Vault + Telemetria Anonimizada SHA-256** |

---

### 5.2. Nosso Verdadeiro Valor de Mercado (Por que o MentorIA Tech se destaca?)

1. **Do "Chat Passivo" para a "Fábrica Estruturada de Aprendizagem":**
   * Ferramentas como o *NotebookLM* ou o *ChatGPT* exigem que o estudante **saiba o que perguntar** (*blank page syndrome*). Um iniciante em transição de carreira que abre um manual de 50 páginas de redes na Oracle Cloud muitas vezes não sabe nem formular a primeira pergunta.
   * O **MentorIA Tech** elimina a barreira do prompt: com 3 cliques (`Perfil` + `Formato` + `Nicho`), ele transforma o documento inteiro em uma trilha pedagógica pronta (`Tutorial`, `Flashcards`, `Quiz`, `Roteiro`, `TL;DR` ou `Resumo`).
2. **Motor B2B / EdTech Integrável (API-First & JSON Schema):**
   * Enquanto concorrentes prendem o conteúdo dentro da própria tela, o **MentorIA Tech** entrega um pacote `PacoteFinal` 100% validado em JSON e persistido na nuvem (OCI), podendo alimentar automaticamente plataformas LMS corporativas (Moodle, Alura, portais internos de onboarding de desenvolvedores) e painéis de BI.
3. **Verificação Determinística de Referências (Auditoria Anti-Alucinação):**
   * Em treinamentos técnicos (infraestrutura em nuvem, segurança, saúde, finanças), uma alucinação pode causar incidentes graves. Nossa camada `_validar_conteudo()` atua como um **auditor determinístico em código Python**: se a IA tentar citar uma página que não estava no chunk recuperado, o pacote é bloqueado antes de chegar ao aluno.
