# Tutorial Didático de Configuração na Oracle Cloud (OCI Always Free) — MentorIA Tech

**Responsável:** Lídia Moura (Lidi) — Líder Técnica  
**Data da última atualização:** 09/11/2026  
**Público:** Liderança Técnica, DevOps e Desenvolvedores da Equipe 26  
**Objetivo:** Configurar com segurança (passo a passo na interface web da OCI) os Grupos, Policies, Buckets do Object Storage e Vault no compartimento `mentoria-tech`, mantendo 100% dentro da camada **Always Free**.

---

## ⚠️ Regras de Ouro antes de começar

1. **Conta Correta:** Acesse a console da **Oracle Cloud Infrastructure (cloud.oracle.com)** (e não o portal de cursos MyLearn).
2. **Região Primária (Home Region):** Crie os Buckets e o Autonomous Database sempre na **Home Region** da conta (ex.: `Brazil East (Sao Paulo)` ou `US East (Ashburn)`), pois os recursos **Always Free** só são gratuitos na região principal da tenancy.
3. **Zero Segredos no Git:** Ao gerar chaves de API, OCIDs ou senhas durante este tutorial, salve-os apenas no gerenciador de senhas / arquivo local `.env` (que está no `.gitignore`).

---

## PASSO 1 — Auditoria e Criação do Compartimento `mentoria-tech`

**O que é um Compartimento (Compartment)?**  
É uma "pasta lógica de segurança" dentro da nuvem da Oracle para isolar os recursos do nosso projeto do restante da conta.

1. No menu superior esquerdo (ícone ☰ "Hambúrguer"), clique em **Identity & Security** (Identidade e Segurança) → **Compartments** (Compartimentos).
2. Verifique se já existe o compartimento **`mentoria-tech`** (ou `mentoria-tec`).
3. **Caso ainda não exista:**
   * Clique em **Create Compartment** (Criar Compartimento).
   * **Name:** `mentoria-tech`
   * **Description:** `Compartimento oficial do MVP MentorIA Tech - Hackathon ONE G10 Equipe 26`
   * **Parent Compartment:** selecione o compartimento raiz `(root)`.
   * Clique em **Create Compartment**.
4. **Copie o OCID do compartimento** (clique em *Copy* ao lado do campo OCID) e guarde no seu bloco de notas local como `OCI_COMPARTMENT_OCID`.

---

## PASSO 2 — Configurar Grupos de Acesso (IAM Identity Domain)

**Por que fazemos isso?**  
Para garantir o **Princípio do Menor Privilégio**: ninguém usa a conta geral de administrador para rodar o código da aplicação, e o grupo público `All Domain Users` não ganha acesso aos nossos buckets.

1. Abra o menu ☰ → **Identity & Security** → **Domains** (Domínios).
2. Clique no domínio ativo (geralmente **Default**).
3. No menu lateral esquerdo do domínio, clique em **Groups** (Grupos).
4. **Auditoria inicial:**
   * Clique no grupo **`Administrators`** e verifique quem está nele (mantenha apenas o dono da conta e a liderança de infraestrutura).
   * Verifique se os demais membros da equipe não estão em `Administrators`.
5. **Crie os grupos do projeto** clicando em **Create group** para cada um abaixo:

| Nome do Grupo | Descrição para colar na Console OCI | Quem adicionar neste grupo |
| :--- | :--- | :--- |
| `mentoria-tech-adm` | `Administradores de infraestrutura do compartimento mentoria-tech` | Lídia Moura, Wagner Campos (Infra/OCI) |
| `mentoria-tech-dev` | `Desenvolvedores Backend/RAG/App com acesso aos buckets e leitura de secrets` | Rodrigo, Vinicius, Leonardo, João, Josiane, Vagner |
| `mentoria-tech-bi` | `Leitura de artefatos e métricas de observabilidade para BI e QA` | Andrea, Lysara, Vagner, Lídia |
| `mentoria-tech-viewer` | `Acesso restrito de visualização da arquitetura no compartimento mentoria-tech` | Convidados ou avaliadores (se necessário) |

---

## PASSO 3 — Criar as Policies (Políticas de Permissão)

**O que é uma Policy na OCI?**  
Um grupo sozinho não tem poder nenhum até escrevermos frases em inglês (Statements) dizendo exatamente o que aquele grupo pode fazer dentro do compartimento `mentoria-tech`.

1. Abra o menu ☰ → **Identity & Security** → **Policies** (Políticas).
2. Na barra lateral esquerda, em **Compartment**, selecione **`mentoria-tech`** (ou o compartimento `(root)` se quiser que a policy fique centralizada, mas apontando apenas para `in compartment mentoria-tech`).
3. Clique em **Create Policy**:
   * **Name:** `mentoria-tech-iam-policy`
   * **Description:** `Políticas de menor privilégio para os grupos do projeto MentorIA Tech`
   * **Compartment:** `mentoria-tech`
4. Ative a chave **Show manual editor** (Mostrar editor manual) e cole exatamente o bloco abaixo:

```text
Allow group mentoria-tech-adm to manage object-family in compartment mentoria-tech
Allow group mentoria-tech-adm to manage vaults in compartment mentoria-tech
Allow group mentoria-tech-adm to manage keys in compartment mentoria-tech
Allow group mentoria-tech-adm to manage secret-family in compartment mentoria-tech
Allow group mentoria-tech-adm to manage autonomous-database-family in compartment mentoria-tech
Allow group mentoria-tech-dev to read buckets in compartment mentoria-tech
Allow group mentoria-tech-dev to manage objects in compartment mentoria-tech where any {target.bucket.name='mentoria-tech-documents', target.bucket.name='mentoria-tech-artifacts', target.bucket.name='mentoria-tech-observability'}
Allow group mentoria-tech-dev to read secret-bundles in compartment mentoria-tech
Allow group mentoria-tech-dev to inspect autonomous-databases in compartment mentoria-tech
Allow group mentoria-tech-bi to read buckets in compartment mentoria-tech
Allow group mentoria-tech-bi to read objects in compartment mentoria-tech where any {target.bucket.name='mentoria-tech-artifacts', target.bucket.name='mentoria-tech-observability'}
Allow group mentoria-tech-viewer to inspect all-resources in compartment mentoria-tech
```
5. Clique em **Create**.

---

## PASSO 4 — Criar os 3 Buckets Privados no OCI Object Storage (Always Free)

**Por que este passo é o mais importante para o Hackathon?**  
O edital da NoCountry exige obrigatoriamente que o MVP persista os documentos originais e os pacotes JSON gerados no **OCI Object Storage (Always Free)**. A camada Always Free oferece **20 GB gratuitos** na classe *Standard*.

1. Abra o menu ☰ → **Storage** (Armazenamento) → **Buckets** (em *Object Storage & Archive Storage*).
2. No seletor **Compartment** à esquerda, confirme que **`mentoria-tech`** está selecionado!
3. Clique em **Create Bucket** e crie os **3 buckets** abaixo (repetindo o processo para cada um):

### Bucket 1: Documentos Brutos
* **Bucket Name:** `mentoria-tech-documents`
* **Default Storage Tier:** `Standard` *(Não escolha Archive!)*
* **Encryption:** `Encrypt using Oracle managed keys` *(Gratuito e automático)*
* ** Clique em **Create**.
* **Visibilidade:** Por padrão, ele nasce como **Private (Privado)**. **Mantenha Privado!**

### Bucket 2: Artefatos Educacionais Gerados (JSON)
* **Bucket Name:** `mentoria-tech-artifacts`
* **Default Storage Tier:** `Standard`
* **Encryption:** `Encrypt using Oracle managed keys`
* **Visibilidade:** `Private`

### Bucket 3: Observabilidade, Feedbacks e Exportações CSV
* **Bucket Name:** `mentoria-tech-observability`
* **Default Storage Tier:** `Standard`
* **Encryption:** `Encrypt using Oracle managed keys`
* **Visibilidade:** `Private`

4. **Onde pegar o `OCI_NAMESPACE`:** Clique em qualquer um dos buckets criados e copie o valor do campo **Namespace** (uma sequência curta de letras/números única da sua conta).

---

## PASSO 5 — Configurar o OCI Vault e guardar as Chaves de API (Secrets)

**O que é o OCI Vault?**  
É o cofre criptografado da Oracle onde guardamos as chaves da API do Gemini, da Groq e a senha do banco para que ninguém precise passar chaves por mensagens ou arquivos soltos.

> 💡 **Atenção sobre Custos (Always Free / Free Tier):** Na criação da chave de criptografia (*Master Encryption Key*), selecione **Protection Mode: Software**! Chaves protegidas por *Software* são gratuitas na OCI (enquanto chaves *HSM* podem consumir créditos após o período trial).

1. Abra o menu ☰ → **Identity & Security** → **Vault**.
2. Confirme que o compartimento **`mentoria-tech`** está selecionado à esquerda.
3. Clique em **Create Vault**:
   * **Name:** `mentoria-tech-vault`
   * **Deixe desmarcada** a opção *Make it a virtual private vault* (pois o Virtual Private Vault é pago!).
   * Clique em **Create Vault** e aguarde ficar `Active`.
4. Entre no `mentoria-tech-vault`, clique em **Master Encryption Keys** no menu lateral e clique em **Create Key**:
   * **Protection Mode:** selecione **`Software`** (Muito importante!).
   * **Name:** `mentoria-tech-master-key`
   * **Key Shape: Algorithm:** `AES` (`256 bits`).
   * Clique em **Create Key** e aguarde ficar `Enabled`.
5. No menu lateral do Vault, clique em **Secrets** → **Create Secret**:
   * **Secret 1 (Chaves Gemini):**
     * **Name:** `mentoria-tech-gemini-api-keys`
     * **Encryption Key:** selecione `mentoria-tech-master-key`
     * **Secret Type Template:** `Plain-Text`
     * **Secret Contents:** cole a(s) chave(s) do Gemini separadas por vírgula (ex.: `chave1,chave2`).
   * **Secret 2 (Chaves Groq Fallback):**
     * **Name:** `mentoria-tech-groq-api-keys`
     * **Encryption Key:** selecione `mentoria-tech-master-key`
     * **Secret Type Template:** `Plain-Text`
     * **Secret Contents:** cole a(s) chave(s) da Groq separadas por vírgula.

---

## PASSO 6 — Inventariar o Autonomous Database (Preparação para o Feedback)

Conforme nosso protocolo, **não executaremos nenhuma alteração destrutiva no banco agora**. Apenas confira na console:

1. Abra o menu ☰ → **Oracle Database** → **Autonomous Database**.
2. Verifique em qual compartimento está a instância já criada pelo Rodrigo (ou pela equipe).
3. Anote apenas os metadados não sensíveis para o inventário da Fase 4:
   * **Display Name / Database Name**
   * **Workload Type** (Transaction Processing / Data Warehouse)
   * **Always Free:** confirmar se o selo `Always Free` está ativo.
   * **State:** `Available` (Disponível) ou `Stopped`.
   * **Network Access:** se exige `mTLS (Wallet)` ou se permite `TLS (Walletless)` com controle de acesso.

Assim que a equipe confirmar o formato final do campo de **Feedback** na reunião de hoje, geraremos o script SQL `CREATE TABLE IF NOT EXISTS` seguro para você colar no **Database Actions -> SQL** da própria console web da OCI!
