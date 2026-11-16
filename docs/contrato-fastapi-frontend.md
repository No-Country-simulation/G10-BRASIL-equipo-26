# NovaMente — Contrato de Integração FastAPI ↔ Frontend

**Versão:** 0.3 (identificadores anônimos por navegador/sessão)  
**Base:** implementação `rag/main.py` testada em 14/11/2026  
**Base URL local:** `http://127.0.0.1:8000`  
**Documentação automática:** `http://127.0.0.1:8000/docs` e `/openapi.json`

## 1. Escopo e identificação provisória

A API **não possui autenticação, contas ou senhas**. O frontend deve gerar automaticamente um UUID de `usuario_id` na primeira visita e persistir no `localStorage`. Deve gerar um UUID de `sessao_id` por sessão de aba, persistido no `sessionStorage`. Os dois campos são **obrigatórios** nas requisições relevantes; não existem mais os valores padrão `teste_local` e `sessao_teste`.

```javascript
function obterOuCriar(storage, chave) {
  let id = storage.getItem(chave);
  if (!id) { id = crypto.randomUUID(); storage.setItem(chave, id); }
  return id;
}
const usuarioId = obterOuCriar(localStorage, 'novamente_usuario_id');
const sessaoId = obterOuCriar(sessionStorage, 'novamente_sessao_id');
```

O mesmo `usuario_id` deve acompanhar geração, listagem, consulta, início de rodada, resposta e histórico. O `sessao_id` deve acompanhar geração, início de rodada e resposta. O backend gera um novo `rodada_id` em `POST /quiz/rodadas`.

**Limitações:** cada perfil de navegador tem seu próprio usuário anônimo; limpar armazenamento ou usar outro dispositivo perde a associação. Não há autenticação: IDs podem ser falsificados e **não protegem dados pessoais**. Uso restrito a ambiente de desenvolvimento controlado; não publicar esta API como serviço aberto. Gerações antigas registradas sob `teste_local` permanecem no SQLite, mas não aparecem para o novo ID anônimo.

O SQLite fica no backend; o frontend comunica-se por HTTP. Índices de questões e alternativas começam em zero.

## 2. Endpoints disponíveis

| Método | Rota | Finalidade | Corpo/Parâmetros |
|---|---|---|---|
| GET | `/health` | Verificar serviço | Nenhum |
| POST | `/geracoes` | Enviar documento e gerar conteúdo | `multipart/form-data` |
| GET | `/quiz` | Listar até 30 Quizzes recentes | Query obrigatória `usuario_id` |
| GET | `/quiz/{geracao_id}` | Consultar questões sem gabarito | Query obrigatória `usuario_id` |
| POST | `/quiz/rodadas` | Iniciar nova rodada | JSON |
| POST | `/quiz/respostas` | Responder e registrar tentativa | JSON |
| GET | `/quiz/{geracao_id}/historico` | Consultar até 100 tentativas | Query obrigatória `usuario_id` |

`GET /` disponibiliza uma interface HTML local de teste, não um endpoint de dados para integração.

## 3. Geração de conteúdo — `POST /geracoes`

**Content-Type:** `multipart/form-data`. **Não** enviar JSON puro nem configurar manualmente o header `Content-Type` no `fetch` com `FormData`.

| Campo | Tipo | Obrigatório | Padrão / valores |
|---|---|---|---|
| `arquivo` | arquivo | Sim | `.pdf`, `.txt` ou `.md`; até 20 MiB |
| `perfil` | string | Não | `Iniciante`; opções `Iniciante`, `Jr/Pleno`, `Tech Lead`, `Gestor` |
| `nivel` | string | Não | `basico`; opções `basico`, `intermediario`, `avancado` |
| `formato` | string | Não | `Quiz`; opções `Quiz`, `Tutorial`, `Flashcards`, `TL;DR`, `Roteiro`, `Resumo` |
| `quantidade_itens` | integer | Não | `5`; intervalo permitido `1`–`100` |
| `usuario_id` | string | **Sim** | UUID anônimo persistente no navegador |
| `sessao_id` | string | **Sim** | UUID por sessão de aba |

**Resposta comum (200):**

```json
{
  "geracao_id": "03dff47d-a7db-4c96-b770-45be626d2a1d",
  "formato": "Quiz",
  "perfil": "Iniciante",
  "nivel_solicitado": "basico",
  "avaliacao_id": "f5d0ec7e-4985-483a-b741-3580fc0258bc",
  "adequacao": {"divergencia": false, "mensagem": null},
  "duracao_ms": 25330.12,
  "questoes": [
    {
      "questao_indice": 0,
      "enunciado": "Qual é a definição de modelo?",
      "alternativas": ["Opção 1", "Opção 2", "Opção 3", "Opção 4"],
      "assunto": "Machine Learning"
    }
  ]
}
```

**Diferenças entre formatos:**

| Formato | Campo de conteúdo | Estrutura principal |
|---|---|---|
| Quiz | `questoes` | Array de `{questao_indice, enunciado, alternativas, assunto}` **sem gabarito** |
| Tutorial | `conteudo` | `{formato, titulo, passos:[{titulo, explicacao, fontes}]}` |
| Flashcards | `conteudo` | `{formato, itens:[{pergunta, resposta, classificacao, fontes}]}` |
| TL;DR | `conteudo` | `{formato, resumo, pontos_chave, fontes}` |
| Roteiro | `conteudo` | `{formato, etapas:[{atividade, duracao_minutos, fontes}]}` |
| Resumo | `conteudo` | `{formato, titulo, secoes:[{titulo, texto, fontes}]}` |

Em `fontes`, cada referência contém `paginas` (array de números) e `chunk_ids` (array de strings).

**Observações:** a requisição é síncrona e pode demorar dezenas de segundos; exibir indicador de progresso indeterminado e evitar envios duplicados. A API retorna o conteúdo na resposta, além de registrá-lo no SQLite. Atualmente **não há** endpoint GET para recuperar por ID conteúdos não-Quiz; o frontend deve conservar a resposta de `/geracoes` se precisar exibi-la novamente durante a sessão.

## 4. Quiz — fluxo e exemplos

### 4.1 Listar Quizzes — `GET /quiz`
Query obrigatória: `usuario_id=<UUID>`. Retorna array, máximo de 30 registros recentes:
`[{"geracao_id": "...", "data_hora": "...", "perfil": "Iniciante", "nivel": "basico"}]`

### 4.2 Consultar Quiz — `GET /quiz/{geracao_id}`
Query obrigatória: `usuario_id=<UUID>`. Retorna `{"geracao_id": "...", "questoes": [...]}` **sem** `indice_resposta_correta` e **sem** `explicacao`.

### 4.3 Iniciar rodada — `POST /quiz/rodadas`
Payload JSON: `{"geracao_id": "...", "usuario_id": "...", "sessao_id": "..."}`.
Resposta (200): `{"rodada_id": "...", "geracao_id": "..."}`.

### 4.4 Responder — `POST /quiz/respostas`
Payload JSON:
`{"geracao_id": "...", "usuario_id": "...", "sessao_id": "...", "rodada_id": "...", "questao_indice": 0, "alternativa_escolhida": 1, "tempo_resposta_segundos": 12.5}`

- **Resposta errada com tentativas restantes (200):** `{"acertou": false, "tentativa_numero": 1, "tentativas_restantes": 2, "questao_encerrada": false}`
- **Resposta após acerto ou 3ª tentativa (200):** inclui `"questao_encerrada": true`, `"indice_resposta_correta": 2`, `"explicacao": "..."`.
- **4ª tentativa ou após acerto na mesma questão/rodada:** HTTP **409**.

### 4.5 Histórico — `GET /quiz/{geracao_id}/historico`
Query obrigatória: `usuario_id=<UUID>`. Retorna até 100 respostas recentes em ordem decrescente de `resposta_id`, com `acertou` como `0` ou `1`.

## 5. Erros e tratamento no frontend

| HTTP | Situação |
|---|---|
| 200 | Sucesso |
| 400 | Geração não é Quiz; rodada não registrada |
| 404 | Quiz inexistente ou não associado ao `usuario_id` informado |
| 409 | Tentativa bloqueada (questão encerrada ou limite atingido) |
| 413 | Upload vazio ou maior que 20 MiB |
| 422 | Arquivo/extensão, perfil, nível, formato, índice ou parâmetros inválidos |
| 500 | Erro interno de geração; consultar logs do servidor |
| 503 | Chave Gemini ausente para o RAG |

## 6. Critérios de aceite

- [ ] Upload e geração de cada um dos seis formatos, com visualização correta.
- [ ] Quiz sem gabarito no primeiro carregamento.
- [ ] Resposta errada mantém gabarito oculto e reduz tentativas restantes.
- [ ] Acerto libera gabarito/explicação e encerra a questão.
- [ ] Três erros liberam gabarito e encerram a questão; quarta tentativa recebe 409.
- [ ] Nova rodada reinicia a contagem e preserva histórico anterior.
- [ ] Histórico mostra `rodada_id`, número de tentativa, assunto e resultado.
- [ ] Interface mostra estado de carregamento, erros HTTP e falhas de rede.
