# Ata de Reunião — 26/10/2026 (Arquitetura, Documento Único e Quadro Kanban)

**Projeto:** MentorIA Tech *(codinome inicial: NovaMente)* — Equipe 26 | Hackathon ONE G10  
**Data:** 26/10/2026  
**Classificação:** Registro público higienizado (sem PII / sem transcrição integral)

---

## 1. Resumo Executivo
* **Arquitetura e Fluxograma:** Vinicius Ferreira apresentou a estrutura do fluxograma arquitetural dividindo envio do documento, processamento backend Python + RAG, orquestração LLM, persistência em nuvem Oracle (OCI) e visualização no frontend.
* **Mitigação de Alucinações e Consumo de Tokens:** A partir de análise levantada por Rodrigo Silva, Josiane da Silva e Vagner Marques, a equipe decidiu focar o MVP no processamento de **um único documento por execução**, reduzindo drasticamente o risco de alucinação cruzada e o estouro de tokens.
* **Organização de Fases e Kanban:** Andrea Gonzalez apresentou a estruturação detalhada das fases operacionais do projeto com etiquetas por área, alinhando a sincronização com o GitHub Projects.

---

## 2. Decisões Alinhadas
1. **Processamento de documento único no MVP:** Cada execução do pipeline indexa e processa um documento técnico por vez.
2. **Fluxo paralelo para o núcleo de IA/RAG:** Desenvolvimento do pipeline RAG/LLM com configuração base testável e evolução iterativa mediante testes quantitativos e qualitativos.
3. **Elaboração de fluxograma oficial e README para a banca:** Garantir documentação clara tanto para avaliadores técnicos quanto para recrutadores/perfis de negócios.
4. **Organização do repositório por áreas:** Manter separação clara entre interface (`app/`), núcleo de RAG (`rag/`), serviços de nuvem (`services/`), dados (`data/`) e documentação (`docs/`).
