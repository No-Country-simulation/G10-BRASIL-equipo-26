# Roteiro Acessível de Vídeo Pitch (Entrega + Demo Day) & Plano de Contingência

**Projeto:** MentorIA Tech — Equipe 26 | Hackathon ONE G10  
**Tempo Alvo:** 2 a 3 minutos (teto máximo de 5 minutos)  
**Estratégia:** Gravação única em **Tema Claro** (tela cheia, sem barras de ferramentas), aproveitável tanto para a entrega oficial quanto para exibição no Demo Day.  
**Documento recomendado para a demo:** Material alinhado diretamente aos **finalistas do G10** (como o documento oficial do desafio/NoCountry ou `rag/Machine_Learning.pdf`), evitando materiais exclusivos de *alumni* G9 que não representam o momento atual da plateia.

---

## 1. Roteiro Acessível Passo a Passo (Linguagem Clara + Inteligência de Mercado)

### [0:00 – 0:45] A Dor Real & O Nosso Diferencial de Mercado (Lídia Moura)
* **Abertura conectando com a plateia:**  
  *"Sabe quando você está estudando tecnologia — ou fazendo transição de carreira — e abre um manual técnico de 30 ou 50 páginas cheio de termos difíceis? Jogar tudo num chat de IA comum parece fácil, mas tem dois problemas sérios: quem está começando muitas vezes nem sabe o que perguntar — é a síndrome da página em branco — e o chat pode misturar informações de fora e inventar respostas sem mostrar onde aquilo estava no texto."*
* **Nossa proposta (baseada na análise de mercado vs. NotebookLM e ChatGPT):**  
  *"O **MentorIA Tech** transforma o 'chat passivo' em uma **fábrica estruturada de estudo** para a área de Tecnologia. Com apenas **3 cliques** (documento + perfil + formato), ele entrega o conteúdo pronto no seu nível — de Iniciante a Tech Lead e Gestor — sem que você precise virar especialista em criar prompts."*

### [0:45 – 1:40] Como Funciona por Baixo dos Panos (Rodrigo Silva)
* **Simplicidade técnica com eficiência:**  
  *"Por trás da tela em **Streamlit**, nossa API **FastAPI** lê documentos `.pdf`, `.md` e `.txt`, divide e busca os trechos certos com **RAG (ChromaDB)** e usa engenharia de prompts enxuta (*CO-STAR* e JSON direto no schema) para economizar até **40% dos tokens de saída**, evitando texto inútil."*
* **Confiabilidade:**  
  *"Cada card ou questão passa por validação estrita (**Pydantic v2**): se a IA tentar citar uma página que não existe no documento, o sistema bloqueia. E se uma API gratuita oscilar, temos roteamento de chaves e fallback automático entre **Gemini** e **Groq**."*

### [1:40 – 3:05] Demonstração Prática no Sistema (Tema Claro)
1. **Cenário 1 — `Iniciante` + `TL;DR` ou `Flashcards`:**
   * *"Escolho o material técnico, seleciono o perfil `Iniciante` e o formato `Flashcards` (ou `TL;DR`). Em segundos, recebo o resumo direto e cada item mostra exatamente de qual página e trecho saiu."*
   * Destacar os botões prontos de exportação (**Markdown**, **JSON** e **CSV para Anki**).
2. **Cenário 2 — `Tech Lead` + `Quiz` Interativo:**
   * *"No modo `Quiz`, o sistema nunca entrega o gabarito antes da hora. Ao iniciar a rodada, o aluno tem até 3 tentativas e recebe explicação fundamentada + histórico de acertos salvo sem coletar dados pessoais (LGPD / Zero PII)."*
3. **Cenário 3 — Oracle Cloud (OCI Always Free):**
   * *"Automaticamente, o conteúdo gerado em JSON estruturado é enviado para o nosso bucket privado **`mentoria-tech-artifacts`** na Oracle Cloud, comprovando a persistência em nuvem."*

### [3:05 – 3:45] Qualidade (QA), Dados e Próximos Passos (Lídia Moura)
* *"Como BI Analyst, garantimos a entrega com **28 testes automatizados aprovados**, relatório analítico em notebook estilo Colab (`pandas`/`seaborn`/`matplotlib`) e exportação limpa em CSV para **Power BI**."*
* *"Para a próxima fase pós-hackathon, já deixamos estruturado o painel ativo de telemetria no Power BI, OCI Vault, bot no Telegram e OCR."*
* **Fechamento:** *"MentorIA Tech: aprender tecnologia com clareza, autonomia e fidelidade às fontes. Obrigado!"*

---

## 2. Versão Offline de Contingência (Plano B do Demo Day)
Para garantir zero imprevistos no palco caso a rede ou as APIs oscilem:
1. **Vídeo MP4 pré-gravado** deste exato roteiro em tela cheia no Tema Claro.
2. **Screenshots reais em alta resolução** (`app/assets/screenshots/`).
3. **Artefatos JSON reais salvos localmente** (`data/oci_fallback/`) demonstrando o `PacoteFinal` e `armazenamento_oci`.
