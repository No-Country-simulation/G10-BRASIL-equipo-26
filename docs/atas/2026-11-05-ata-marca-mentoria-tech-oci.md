# Ata de Reunião — 05/11/2026 (Definição Oficial da Marca MentorIA Tech, OCI e Resiliência)

**Projeto:** MentorIA Tech — Equipe 26 | Hackathon ONE G10  
**Data:** 05/11/2026  
**Classificação:** Registro público higienizado (sem PII / sem transcrição integral)

---

## 1. Resumo Executivo
* **Aprovação Oficial do Nome e Identidade Visual (`MentorIA Tech`):** Lysara Pinheiro apresentou as opções de logomarca e identidade visual baseadas no Brandbook. Em votação colegiada, a equipe aprovou o nome oficial **MentorIA Tech** (layout institucional minimalista) e adotou o design com o **cérebro ilustrado como mascote oficial** do projeto.
* **Demonstração Prática no Google Colab:** Rodrigo Silva demonstrou a execução ponta a ponta do pipeline RAG + LLM gerando os produtos educacionais em menos de 1 minuto com validação Pydantic e salvamento estruturado.
* **Governança na Oracle Cloud Infrastructure (OCI):** Lídia Moura apresentou a estruturação do compartimento do projeto na tenancy OCI (com Wagner Campos), definindo a separação de grupos com políticas de menor privilégio e a criação de buckets dedicados para documentos brutos, artefatos gerados e observabilidade.
* **Engenharia de Resiliência e UX:** Lídia Moura propôs o roteamento com múltiplas chaves/provedores de API (fallback) para proteger a demonstração contra limites de tokens gratuitos, além de mensagens de erro amigáveis na interface para arquivos incompatíveis ou sem camada de texto.

---

## 2. Decisões Alinhadas
1. **Identidade Oficial:** Adoção do nome **MentorIA Tech**, logomarca principal e mascote oficial.
2. **Nicho Central:** Posicionamento focado em educação e capacitação em tecnologia.
3. **Segurança e Governança OCI:** Uso de Object Storage privado e grupos com policies restritas ao compartimento do projeto.
4. **Prioridade Crítica de Fechamento do MVP:** Priorizar a conexão fim a fim (Extrator + Pipeline RAG/LLM + Interface Streamlit + Persistência OCI Object Storage) e os testes automatizados para a semana final antes do Demo Day.
