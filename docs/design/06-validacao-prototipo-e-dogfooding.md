# Validação do Protótipo & Dogfooding — MentorIA Tech

* **Etapa de Design:** Prototipação Navegável & Testes de Usabilidade (Validação)
* **Método Aplicado:** *Dogfooding* Estruturado (Testes internos realizados pelos integrantes do Grupo 10-Equipe 26 — estudantes e desenvolvedores do programa **ONE - Oracle Next Education**, que representam diretamente a persona alvo do produto).
* **Artefato Validado:** Protótipo funcional local em HTML/CSS/JS (`index.html`).

---

## 1. Contexto da Validação

Durante o desenvolvimento acelerado do Hackathon, a equipe construiu um **protótipo funcional navegável** simulando o fluxo completo de ponta a ponta (ingestão de fontes em `TXT`/`MD`/`PDF`, parametrização no Estúdio de Criação, geração de prévias interativas de *Flashcards*, *Quiz*, *Tutorial*, *Resumo* e *Roteiro*, e exportação em `JSON`).

Como os próprios membros do time são estudantes ativos do programa **ONE** enfrentando a dor real de estudar documentações técnicas extensas, aplicamos sessões de **Dogfooding** para validar a arquitetura de informação e identificar atritos antes da entrega do MVP.

---

## 2. Hipóteses Testadas e Resultados (Matriz CSD Atualizada)

| Hipótese Avaliada | Resultado Observado no Protótipo | Decisão de Design / Ajuste Aplicado |
| :--- | :--- | :--- |
| **H1. Separação entre *Biblioteca de Fontes* e *Biblioteca de Conteúdo*:** O usuário entende a diferença entre o material bruto e o estudo gerado? | **Validado com sucesso.** A metáfora de *Insumo (Biblioteca)* $\rightarrow$ *Transformação (Estúdio)* $\rightarrow$ *Acervo Pronto (Meus Conteúdos)* mostrou-se clara e evitou misturar PDFs originais com baralhos de flashcards. | Mantida a arquitetura em 4 pilares na navegação lateral, reforçada pelo breadcrumb dinâmico no topo. |
| **H2. Clareza dos parâmetros no *Estúdio de Criação*:** Os campos de configuração ajudam ou atrasam a geração do estudo? | **Atrito identificado.** O campo *"Contexto de aplicação / Setor"* (ex.: Fintech, Saúde, E-commerce) gerou dúvida sobre sua real utilidade, uma vez que a plataforma já está nichada para educação técnica em tecnologia. | **Remoção do parâmetro "Contexto de aplicação"** no MVP final, simplificando o formulário para *Material de origem*, *Perfil do destinatário*, *Nível de detalhe* e *Formato pedagógico*. |
| **H3. Valor da Pré-visualização antes de salvar/exportar:** O Split-View no Estúdio ajuda a validar o resultado? | **Validado.** Poder testar o flip dos flashcards e revelar respostas do quiz imediatamente ao lado das configurações aumentou a sensação de controle sobre a IA. | Mantido o layout *Split-View* (Configuração à esquerda, Prévia interativa à direita) como padrão da tela. |
| **H4. Transparência sobre processamento RAG/PDF:** O usuário entende o status dos arquivos enviados? | **Validado.** Distinguir visualmente arquivos prontos (`TXT`/`MD`) de arquivos que aguardam extração no backend (`PDF`) evitou frustração durante os testes locais. | Padronizados badges de status e mensagens explicativas nos estados vazios (*Empty States*). |

---

## 3. Roteiro de Teste de Usabilidade (Para Validação Externa com Alunos ONE)

Para expandir a validação com colegas de outras turmas/grupos do programa ONE após o hackathon, utiliza-se o roteiro enxuto abaixo (duração: ~10 minutos por participante):

### Tarefas do Participante
1. **Ingestão:** *"Você acabou de baixar uma documentação técnica sobre Spring Boot ou OCI. Adicione esse material na plataforma."* (Observa-se se encontra a **Biblioteca de Fontes** sem ajuda).
2. **Criação:** *"Gere um conjunto de Flashcards e um Tutorial passo a passo focados em nível iniciante."* (Observa-se a fluidez no **Estúdio de Criação** e compreensão dos parâmetros).
3. **Consumo & Exportação:** *"Teste os flashcards gerados, localize onde ficam salvos seus estudos anteriores e exporte o resultado."* (Observa-se o uso da **Pré-visualização** e da **Biblioteca de Conteúdo**).

### Métricas-Chave de Sucesso (KPIs de UX)
* **Taxa de Sucesso na Tarefa (Task Success Rate):** $\ge 85\%$ dos participantes completam o fluxo Upload $\rightarrow$ Estúdio $\rightarrow$ Estudo sem intervenção do moderador.
* **Tempo até o Primeiro Valor (Time-to-First-Study):** $< 90$ segundos entre acessar a plataforma e visualizar o primeiro artefato gerado.
* **Clareza de Navegação:** Zero confusão entre onde subir arquivos (*Biblioteca de Fontes*) e onde revisar materiais prontos (*Meus Conteúdos*).