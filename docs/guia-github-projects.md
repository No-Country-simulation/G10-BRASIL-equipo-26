# Guia Prático: Como Sincronizar Branches, Issues e Pull Requests com o GitHub Projects (`g10-equipo26`)

**Responsável:** Lídia Moura (Lidi) — Líder Técnica  
**Data da última atualização:** 09/11/2026  
**Público:** Todos os integrantes da Equipe 26

---

## 1. Entendendo a Tríade do GitHub (Repositório + Issues/PRs + Projects)

Para que o trabalho de cada pessoa apareça no quadro Kanban do time e na lista oficial de contribuidores do repositório:
* **Branch (Ramificação):** onde você desenvolve sua tarefa sem afetar a `main`.
* **Pull Request (PR):** o pedido formal para mesclar sua branch na `main` (é o PR aprovado que registra você como contribuidor ativo!).
* **GitHub Projects (`g10-equipo26`):** o painel visual (Tabela / Kanban) que acompanha o status (`Backlog`, `Ready`, `In Progress`, `In Review`, `Done`, `Blocked`) das **Issues** e dos **Pull Requests**.

---

## 2. Passo a Passo para Vincular sua Nova Branch / PR ao Projects

### Passo 1: Enviar a branch para o GitHub (após revisão local)
```powershell
git push -u origin docs/mentoria-tech-integracao
```

### Passo 2: Abrir o Pull Request vinculando ao Quadro `g10-equipo26`
1. Acesse o repositório no navegador: `https://github.com/No-Country-simulation/G10-BRASIL-equipo-26`.
2. Clique no botão verde **Compare & pull request** da branch `docs/mentoria-tech-integracao`.
3. Na barra lateral direita da tela de criação do PR:
   * **Reviewers:** selecione pelo menos 1 colega da equipe para revisar.
   * **Assignees:** clique em *assign yourself* (atribuir a você).
   * **Labels:** adicione as etiquetas da frente (ex.: `documentation`, `oci`, `qa`).
   * **Projects:** clique na engrenagem ao lado de **Projects** e marque **`g10-equipo26`** (ou `Equipo 26`).
   * Assim que selecionado, escolha o Status **`In Review`** (Em Revisão).

### Passo 3: Fechar tarefas automaticamente no Kanban quando o PR for aprovado
Se existirem cartões (Issues) abertos no GitHub Projects referentes ao trabalho entregue na branch (por exemplo, Issue `#12` e Issue `#18`), inclua no texto de descrição do seu Pull Request:

```markdown
Closes #12
Closes #18
```

Quando o Pull Request receber o **Merge**, o próprio GitHub moverá os cartões `#12`, `#18` e o próprio PR automaticamente para a coluna **Done (Concluído)** no GitHub Projects!

---

## 3. Regra Importante de Salvamento nas Views do GitHub Projects

Quando você criar um filtro novo, ordenar uma coluna ou agrupar por Área/Fase dentro da aba **Projects** do GitHub:
* Observe se apareceu um botão azul **Save changes** (Salvar alterações) no canto superior direito da aba da tabela/Kanban.
* Sempre clique em **Save changes**; caso contrário, a alteração visual fica apenas no seu navegador e os outros 9 integrantes da equipe não verão a mudança!
