# Ata de Reunião — 09/11/2026 (Revisão do MVP, Governança OCI Vault, Alinhamentos de Escopo e Demo Day)

**Projeto:** MentorIA Tech — Equipe 26 | Hackathon ONE G10  
**Data:** 09/11/2026  
**Classificação:** Registro público higienizado (sem PII / sem transcrição integral)

---

## 1. Resumo Executivo
* **Revisão de Código e Governança Documental:** Lídia Moura apresentou a branch `docs/mentoria-tech-integracao` contendo o README atualizado com a marca MentorIA Tech, a arquitetura técnica, as atas higienizadas, as métricas e o plano de QA/STAR. Foi alinhada a substituição das logos em JPG/WebP por formatos em PNG/SVG com fundo transparente pela Lysara Pinheiro.
* **Infraestrutura OCI e Centralização no OCI Vault:** Lídia Moura informou a criação do compartimento `mentoria-tech` em sua tenancy própria (contornando problemas anteriores de permissão), com grupos e políticas de menor privilégio. Ficou alinhada a adoção do **OCI Vault** para armazenar de forma segura as chaves de API da equipe em pool com fallback (Gemini principal -> Groq contingência), eliminando credenciais dispersas.
* **Escopo Enxuto do MVP e Foco em Tecnologia:** A equipe concordou em manter a implementação focada estritamente nos requisitos obrigatórios do edital. Foi decidida a **remoção do campo de nicho no backend** para focar 100% no setor de tecnologia e educação técnica, e o adiamento da interface ativa de feedback para o pós-MVP.
* **Extrator de Documentos e Conexão Frontend/Backend:** Vinicius Ferreira confirmou que o extrator está pronto e funcional, e Rodrigo Silva informou que o pipeline com testes de LLM por perfil e nível está estruturado, restando a integração final com a interface Streamlit do Wagner Campos.
* **Preparação para o Demo Day:** Confirmação do calendário oficial: primeiro Demo Day em **24 de novembro** (seleção dos 10 melhores) e apresentação final em **26 de novembro**. Planejamento de vídeo demonstrativo de até 5 minutos como backup de segurança e agendamento de ensaio técnico prévio no Microsoft Teams.

---

## 2. Decisões Alinhadas
1. **Foco Estrito no MVP Funcional:** Priorizar os requisitos eliminatórios do edital NoCountry (Extrator + RAG + LLM + Streamlit + OCI Object Storage).
2. **Segurança via OCI Vault:** Centralização de todas as chaves de API no OCI Vault da tenancy `mentoria-tech` com failover multi-chaves (Gemini/Groq).
3. **Remoção do Campo de Nicho no Backend:** Manutenção do foco exclusivo em tecnologia.
4. **Classificação do Feedback de Usuário como Pós-MVP:** A coleta ativa de feedback com 5 estrelas e comentários foi modelada no banco, mas fica postergada para pós-entrega do MVP básico.
5. **Logística do Demo Day:** Produção de vídeo de demonstração de 5 minutos, definição dos apresentadores via enquete e realização de ensaio técnico no Teams antes da apresentação.

---

## 3. Ações e Próximos Passos Registrados
* **Lídia Moura:** Configurar a saída do pipeline para os buckets do OCI Object Storage e estruturar o conector seguro do OCI Vault.
* **Lysara Pinheiro:** Disponibilizar os logotipos institucionais e do mascote em PNG transparente e SVG.
* **Rodrigo Silva / Vinicius Ferreira / Leonardo Santos:** Finalizar os testes integrados do extrator e remover o campo de nicho no backend.
* **Wagner Campos / Lídia Moura:** Conectar a interface Streamlit ao pipeline real em `rag/pipeline/`.
* **Equipe:** Enviar chaves de API para composição do pool de contingência no OCI Vault e gravar o vídeo oficial de demonstração.
