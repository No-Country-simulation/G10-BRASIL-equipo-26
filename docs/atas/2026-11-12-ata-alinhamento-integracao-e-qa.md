# Ata de Reunião — 12/11/2026 (Alinhamento Técnico do MVP, Roteamento de IA, OCI e Preparação para o Merge)

**Projeto:** MentorIA Tech — Equipe 26 | Hackathon ONE G10  
**Data:** 12/11/2026  
**Classificação:** Registro público higienizado (sem PII / sem transcrição integral)

---

## 1. Resumo Executivo
* **Status do Pull Request e Validação Local:** Lídia Moura apresentou o Pull Request da branch `docs/mentoria-tech-integracao`, contendo a suíte de testes de QA, a validação no Jupyter Notebook, a integração do OCI Object Storage e os exportadores para o Power BI. Foi alinhado o roteiro para execução dos testes locais pela equipe.
* **Roteamento de IA e Resiliência (Multi-Chaves):** Apresentação da implementação do pool dinâmico de chaves de API com alternância automática e contingência entre Google Gemini (`gemini-3.8-flash`) e Groq (`openai/gpt-oss-120b`). Os testes comprovaram a estabilidade contra sobrecargas (erros 503/429) e mitigaram o esgotamento de cotas diárias durante o desenvolvimento.
* **Governança OCI e Definição de Arquitetura no MVP:** Diante da restrição técnica de quota da conta Always Free da Oracle Cloud (limite de 1 Vault por tenancy já alocado em projeto anterior), a equipe acordou manter o gerenciamento de credenciais via variáveis de ambiente seguras (`.env` local e Secrets do Streamlit) no MVP, postergando a centralização no OCI Vault para a fase pós-hackathon. O bucket de artefatos foi ratificado como `mentoria-tech-artifacts`.
* **Métricas Internas e Exportação para Power BI:** Foi validada a exportação de dados analíticos para monitoramento de latência, taxa de acerto do RAG e volume de requisições. O painel do Power BI permanece de uso estritamente interno da equipe para auditoria do MVP.
* **Identidade Visual e Logística do Demo Day:** Lysara Pinheiro e equipe definiram o ajuste de orientação do plano de fundo institucional para o Demo Day, incluindo as marcas parceiras (NoCountry, Oracle e Alura). Com base nas novas orientações do edital permitindo até 3 apresentadores, ficou acordado que a condução do pitch e demonstração técnica será realizada em conjunto por Rodrigo Silva e Lídia Moura.
* **Estratégia de Sincronização e Merge na `main`:** Para evitar divergências de código com as alterações recentes na branch principal, ficou acordada a sincronização imediata da branch de documentação e integração (`docs/mentoria-tech-integracao`) com a `main`.

---

## 2. Decisões Alinhadas
1. **Sincronização e Merge Imediato:** Realizar a atualização da branch e o merge formal do PR na `main` no dia 13/11, garantindo que toda a equipe trabalhe sobre a mesma base estável.
2. **Modelo Híbrido de IA no MVP:** Adoção oficial do Gemini 3.8 Flash como provedor primário e Groq como fallback imediato para garantir 100% de disponibilidade no Demo Day.
3. **Escopo do Power BI:** O dashboard servirá para governança e observabilidade interna da equipe durante a avaliação, sem exibição direta ao usuário final no MVP.
4. **Padronização do Bucket OCI:** Todo o armazenamento de artefatos gerados pelo backend deve apontar uniformemente para o bucket `mentoria-tech-artifacts`.
5. **Divisão de Apresentadores no Pitch:** Condução conjunta do Demo Day entre Lídia Moura e Rodrigo Silva, com ensaio técnico prévio via Microsoft Teams.

---

## 3. Ações e Próximos Passos Registrados
* **Lídia Moura:** Sincronizar a branch com a `main`, incluir a suíte de testes de QA (`test_qa_pipeline.py`), o notebook de validação (`validacao_pipeline_mentoria_tech.ipynb`) e orientar as configurações de segredos no Streamlit Cloud.
* **Wagner Campos:** Atualizar o apontamento do bucket no frontend (`app/main.py`) para `mentoria-tech-artifacts` e cadastrar as variáveis no painel de Secrets do Streamlit.
* **Rodrigo Silva:** Validar localmente as chamadas do pipeline com os novos modelos de LLM e apoiar na estrutura do roteiro da apresentação.
* **Lysara Pinheiro:** Finalizar o design do plano de fundo oficial do Demo Day com os logotipos dos parceiros e centralização segura para compartilhamento de tela.
* **Andrea Gonzalez:** Acompanhar as diretrizes oficiais de submissão da NoCountry e apoiar na revisão da documentação pública.
* **Equipe:** Participar de ensaio técnico do pitch na semana do Demo Day e revisar os READMEs multilíngues.

