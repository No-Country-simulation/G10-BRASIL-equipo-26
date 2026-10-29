# Política de Divulgação Responsável de Vulnerabilidades

## 1. Versões Suportadas

Apenas a versão principal mantida no repositório oficial recebe atualizações de segurança e correções ativas.

| Versão                     | Suportada |
| :---                       | :---      |
| MVP (main branch)          |  Sim      |
| < 1.0.0 (branches antigas) |  Não      |

---

## 2. Como Relatar uma Vulnerabilidade de Forma Segura

Se você identificar uma falha de segurança, vazamento de credencial ou vulnerabilidade no **NovaMente | G10-BRASIL-equipo-26** 
(no pipeline de RAG, na integração com o OCI Object Storage ou na interface), por favor, **não abra uma Issue pública no GitHub**.

### Canal de Comunicação Privado:
* **E-mail seguro para contato:** [andrea_denardi@hotmail.com](mailto:andrea_denardi@hotmail.com)
* **Assunto da mensagem:** `[SECURITY] Relatório de Vulnerabilidade - Projeto NovaMente | G10-BRASIL-equipo-26`

---

## 3. O que Incluir no seu Relatório

Para nos ajudar a triar e corrigir o problema rapidamente, inclua as seguintes informações no e-mail:

1. **Descrição da vulnerabilidade:** Qual é a falha identificada (ex.: exposição de credencial, injeção de prompt, bypass de validaçãoJSON, permissão indevida no Bucket OCI).
2. **Passos para reproduzir:** Instruções detalhadas ou um script simples de prova de conceito (*Proof of Concept - PoC*).
3. **Impacto estimado:** O risco que a falha representa para o sistema ou para os dados gravados.
4. **Sua identificação (opcional):** Como você gostaria de ser creditado nos agradecimentos de segurança (*Agradecimentos / Hall of Fame*).

---

## 4. Prazos e Compromisso de Resposta (SLAs)

A equipe do projeto se compromete com os seguintes prazos:

* **Confirmação de recebimento:** Em até 48 horas úteis após o envio do e-mail.
* **Avaliação inicial do risco:** Em até 5 dias úteis.
* **Publicação do ajuste/patch:** O tempo varia conforme a gravidade, mas buscaremos corrigir falhas críticas em até 14 dias.

---

## 5. Diretrizes de Pesquisa Responsável (Safe Harbor)

Para proteger você e o projeto, solicitamos que durante os testes de segurança:

* **Não realize ataques destruidores:** Evite testes de Negação de Serviço (DoS/DDoS).
* **Não acesse dados de terceiros:** Limite seus testes apenas aos seus próprios artefatos ou documentos de teste.
* **Respeite a gratuidade do sistema:** Não execute testes de estresse automatizados que estourem as cotas gratuitas das APIs de LLM ou da camada *Always Free* da OCI.
* **Manutenção do sigilo:** Mantenha a vulnerabilidade em sigilo até que a equipe tenha publicado a correção.

---

## 6. Agradecimentos aos Pesquisadores

Agradecemos à comunidade de software livre e de segurança por nos ajudar a manter o **NovaMente | G10-BRASIL-equipo-26** seguro. 

Todos os pesquisadores que relatarem falhas de forma responsável serão citados no arquivo `CREDITS.md` do projeto.




