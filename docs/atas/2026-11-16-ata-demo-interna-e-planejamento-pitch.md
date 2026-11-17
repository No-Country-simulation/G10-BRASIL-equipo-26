# Ata de Reunião — 16/11/2026 (Demonstração Ponta a Ponta, Estratégia de Pitch e Alinhamentos Finais)

**Projeto:** MentorIA Tech — Equipe 26 | Hackathon ONE G10  
**Data:** 16/11/2026  
**Classificação:** Registro público higienizado (sem PII / sem informações pessoais ou sensíveis)

---

## 1. Resumo Executivo
* **Demonstração Ponta a Ponta do MVP:** Lídia Moura e Wagner Campos validaram ao vivo o fluxo completo integrando o frontend Streamlit (`app/main.py`), a API FastAPI (`rag/main.py`), a geração de conteúdos (incluindo Quiz interativo com limite de 3 tentativas e citação de chunks RAG), a persistência local em SQLite e o envio confirmado para o bucket privado na Oracle Cloud Infrastructure (`mentoria-tech-artifacts`).
* **Desempenho das LLMs e Proposta de Prioridade:** Lídia Moura e Rodrigo Silva observaram maior estabilidade e velocidade nas respostas do modelo via **Groq** em comparação às instabilidades/retries recentes do **Gemini**, propondo priorizar o Groq como provedor primário com Gemini em contingência.
* **Tema Claro no Demo Day:** A equipe aprovou manter o **Tema Claro (Light)** como padrão oficial para o vídeo de demonstração e o Demo Day, evitando problemas de contraste observados no tema escuro.
* **Métricas de Acessibilidade e SEO:** Wagner Campos relatou pontuação máxima (100%) em SEO e acessibilidade na inspeção via Lighthouse, apontando melhorias futuras de performance e metas de otimização.
* **Estratégia do Pitch e Prazos Finais:** A equipe decidiu utilizar vídeo pré-gravado (2 a 3 minutos, respeitando o teto de 5 minutos) para evitar atrasos de geração ao vivo durante o Demo Day. Ficou definido o prazo interno de **sexta-feira** para fechamento do vídeo e **domingo (22/11)** para submissão final e avaliações na plataforma.

---

## 2. Decisões Alinhadas
1. **Envio Garantido do MVP Atual:** Submeter a versão atual já validada dentro do prazo oficial, mantendo melhorias incrementais até a apresentação.
2. **Tema Claro na Apresentação:** Utilizar exclusivamente o Tema Claro do Streamlit nas gravações e demonstrações oficiais.
3. **Divisão do Pitch:** Lídia Moura conduzirá a introdução, contexto de mercado e experiência do usuário; Rodrigo Silva apresentará a arquitetura técnica e o fluxo RAG.
4. **Uso de Vídeo Pré-Gravado:** Gravar a demonstração em tela cheia (sem barras de ferramentas) para garantir fluidez dentro do limite de tempo.
5. **Priorização de LLM (em avaliação técnica):** Avaliar a inversão da ordem dos provedores para `Groq -> Gemini` visando menor latência na resposta ao usuário.
6. **Governança de Prazos e Avaliações:** Concluir vídeo de pitch até sexta-feira; realizar ensaios conjuntos (quinta-feira no Meet para foto oficial com fundo da equipe e ensaio técnico no Teams); concluir avaliações 360º/pares na plataforma até domingo (22/11).

---

## 3. Ações e Próximos Passos Registrados
* **Lídia Moura & Rodrigo Silva:** Gravar a demonstração do MVP (sem barras de ferramentas), finalizar o roteiro do pitch e ensaiar o tempo de apresentação (até 5 min).
* **Lídia Moura:** Publicar o relatório final de QA e evidências, revisar metadados/documentação de entrega e manter melhorias analíticas (Power BI / notebook Colab) para consolidação final.
* **Wagner Campos:** Finalizar o deploy do frontend com as variáveis/chaves configuradas em ambiente seguro e aplicar melhorias incrementais de performance.
* **Andrea Gonzalez:** Coordenar a organização do vídeo final (incluindo suporte multilíngue quando aplicável), preparar orientações para o ensaio em tela cheia no Microsoft Teams e acompanhar o cronograma até domingo (22/11).
* **Equipe (Rodrigo, Wagner, Leonardo e demais membros):** Atualizar datas e status no board do GitHub Projects, disponibilizar chaves de API para o ambiente de deploy via canal privado seguro e realizar as avaliações de pares dentro do prazo.
