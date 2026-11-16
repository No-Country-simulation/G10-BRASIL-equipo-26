"""Máquina de estados e interface interativa do Quiz (contrato FastAPI v0.3)."""

import html
import time
from datetime import datetime
from typing import Any

import streamlit as st

import api_client
from api_client import ApiError


def _letra_alternativa(indice: int) -> str:
    """Converte índice zero-based em letra A..F."""
    return chr(65 + indice) if 0 <= indice < 26 else str(indice + 1)


def _estado_inicial_questoes(qtd: int) -> dict[int, dict[str, Any]]:
    """Cria estrutura limpa de controle local de tentativas para cada questão."""
    agora = time.time()
    return {
        i: {
            "tentativas": [],
            "restantes": 3,
            "encerrada": False,
            "indice_correto": None,
            "explicacao": None,
            "inicio_ts": agora,
        }
        for i in range(qtd)
    }


def carregar_quiz(
    geracao_id: str,
    usuario_id: str,
    questoes: list[dict[str, Any]] | None = None,
    session: Any = None,
) -> dict[str, Any]:
    """Inicializa ou recupera o estado do Quiz em `st.session_state['quiz']`."""
    mapa_quiz = st.session_state.setdefault("quiz", {})
    existente = mapa_quiz.get(geracao_id)
    if existente and existente.get("questoes"):
        return existente

    if questoes is None:
        dados = api_client.consultar_quiz(geracao_id, usuario_id, session=session)
        questoes = dados.get("questoes") or []

    estado = {
        "questoes": questoes,
        "rodada_id": None,
        "questoes_estado": _estado_inicial_questoes(len(questoes)),
        "historico": None,
    }
    mapa_quiz[geracao_id] = estado
    return estado


def iniciar_nova_rodada(
    geracao_id: str,
    usuario_id: str,
    sessao_id: str,
    session: Any = None,
) -> dict[str, Any]:
    """Chama `POST /quiz/rodadas`, reinicia contadores locais e recarrega o histórico."""
    estado = st.session_state["quiz"][geracao_id]
    resp = api_client.iniciar_rodada(geracao_id, usuario_id, sessao_id, session=session)
    estado["rodada_id"] = resp["rodada_id"]
    estado["questoes_estado"] = _estado_inicial_questoes(len(estado["questoes"]))
    try:
        estado["historico"] = api_client.obter_historico(geracao_id, usuario_id, session=session)
    except ApiError:
        pass
    return resp


def aplicar_resposta(
    geracao_id: str,
    questao_indice: int,
    alternativa_escolhida: int,
    resp: dict[str, Any],
) -> None:
    """Atualiza o estado local da questão apenas com dados retornados pelo servidor."""
    estado = st.session_state["quiz"][geracao_id]
    q_est = estado["questoes_estado"][questao_indice]

    q_est["tentativas"].append(
        {
            "alternativa": alternativa_escolhida,
            "acertou": bool(resp.get("acertou")),
            "n": int(resp.get("tentativa_numero", len(q_est["tentativas"]) + 1)),
        }
    )
    q_est["restantes"] = int(resp.get("tentativas_restantes", 0))
    q_est["encerrada"] = bool(resp.get("questao_encerrada", False))

    if q_est["encerrada"]:
        q_est["indice_correto"] = resp.get("indice_resposta_correta")
        q_est["explicacao"] = resp.get("explicacao")
    else:
        q_est["inicio_ts"] = time.time()

    # Invalida cache local de histórico para atualização imediata após rerun
    estado["historico"] = None


def tratar_erro_quiz(err: ApiError, geracao_id: str, questao_indice: int) -> None:
    """Trata erros HTTP específicos do fluxo do Quiz (409, 400, 404, etc.)."""
    estado = st.session_state["quiz"][geracao_id]
    q_est = estado["questoes_estado"].get(questao_indice)

    if err.status == 409:
        if q_est is not None:
            q_est["encerrada"] = True
            q_est["restantes"] = 0
        st.warning(f"🔒 {err.mensagem_amigavel}")
    elif err.status == 400 and "rodada" in err.detalhe.lower():
        estado["rodada_id"] = None
        st.warning(f"⚠️ {err.mensagem_amigavel}")
    else:
        st.error(f"❌ {err.mensagem_amigavel}")


def _exibir_feedback_questao(q: dict[str, Any], q_est: dict[str, Any]) -> None:
    """Mostra feedback da última tentativa; nunca exibe gabarito antes do encerramento."""
    tentativas = q_est.get("tentativas") or []
    if not tentativas:
        return

    ultima = tentativas[-1]
    n = ultima["n"]
    alts = q.get("alternativas") or []

    if q_est["encerrada"] and ultima["acertou"]:
        exp = q_est.get("explicacao") or ""
        st.success(f"✅ **Correto na tentativa {n}!** {exp}")
    elif q_est["encerrada"] and not ultima["acertou"]:
        c_idx = q_est.get("indice_correto")
        if c_idx is not None and 0 <= c_idx < len(alts):
            gabarito_txt = f"{_letra_alternativa(c_idx)}) {alts[c_idx]}"
        else:
            gabarito_txt = "—"
        exp = q_est.get("explicacao") or ""
        st.error(
            f"❌ **Limite de 3 tentativas atingido.** Resposta correta: **{gabarito_txt}**\n\n"
            f"> {exp}"
        )
    else:
        st.warning(
            f"⚠️ **Resposta incorreta** (tentativa {n} de 3). "
            f"Tentativas restantes: **{q_est['restantes']}**."
        )


@st.fragment
def _renderizar_questao_fragment(
    geracao_id: str,
    idx: int,
    usuario_id: str,
    sessao_id: str,
    key_prefix: str = "quiz",
) -> None:
    """Renderiza uma questão isolada em fragmento para resposta rápida sem recarregar tudo."""
    estado = st.session_state["quiz"][geracao_id]
    q = estado["questoes"][idx]
    q_est = estado["questoes_estado"][idx]
    rodada_id = estado.get("rodada_id")
    alts = q.get("alternativas") or []
    assunto = q.get("assunto") or (q.get("classificacao") or {}).get("assunto") or "Geral"

    tentativas = q_est["tentativas"]
    ja_acertou = any(t["acertou"] for t in tentativas)
    encerrada = bool(q_est["encerrada"])
    desabilitada = (rodada_id is None) or encerrada

    if encerrada and ja_acertou:
        status_pill = "<span class='nm-pill nm-pill-mint'>✅ Acertou</span>"
    elif encerrada:
        status_pill = "<span class='nm-pill nm-pill-pink'>🔒 Encerrada (3/3)</span>"
    elif tentativas:
        status_pill = f"<span class='nm-pill nm-pill-lavender'>🔄 Tentativa {len(tentativas)}/3 · Restam {q_est['restantes']}</span>"
    else:
        status_pill = "<span class='nm-pill nm-pill-lavender'>📝 3 tentativas disponíveis</span>"

    st.markdown(
        f"<div style='margin-bottom: 6px;'>"
        f"<span class='nm-pill nm-pill-mint'>📚 {html.escape(str(assunto))}</span>"
        f"{status_pill}"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"**{idx + 1}. {q.get('enunciado', '')}**")

    erradas_previas = {t["alternativa"] for t in tentativas if not t["acertou"]}
    if erradas_previas:
        marcadas = ", ".join(_letra_alternativa(a) for a in sorted(erradas_previas))
        st.caption(f"Alternativas já tentadas sem sucesso nesta rodada: {marcadas}")

    form_key = f"form_{key_prefix}_{geracao_id}_{rodada_id or 'sem'}_{idx}"
    radio_key = f"radio_{key_prefix}_{geracao_id}_{rodada_id or 'sem'}_{idx}"

    with st.form(key=form_key):
        escolha = st.radio(
            f"Alternativas da questão {idx + 1}:",
            options=list(range(len(alts))),
            format_func=lambda j: f"{_letra_alternativa(j)}) {alts[j]}" + (" (já tentada)" if j in erradas_previas else ""),
            index=None,
            disabled=desabilitada,
            key=radio_key,
            label_visibility="collapsed",
        )
        enviou = st.form_submit_button(
            "Responder" if not encerrada else "Questão encerrada",
            type="primary",
            disabled=desabilitada,
        )

    if enviou:
        if escolha is None:
            st.warning("Selecione uma alternativa antes de enviar.")
        elif escolha in erradas_previas:
            st.warning("Você já tentou essa alternativa nesta rodada. Escolha outra para não gastar tentativa.")
        else:
            tempo_s = max(0.0, time.time() - float(q_est.get("inicio_ts", time.time())))
            try:
                resp = api_client.responder_questao(
                    geracao_id=geracao_id,
                    usuario_id=usuario_id,
                    sessao_id=sessao_id,
                    rodada_id=str(rodada_id),
                    questao_indice=idx,
                    alternativa_escolhida=int(escolha),
                    tempo_resposta_segundos=round(tempo_s, 2),
                )
                aplicar_resposta(geracao_id, idx, int(escolha), resp)
                st.rerun(scope="app")
            except ApiError as err:
                tratar_erro_quiz(err, geracao_id, idx)

    _exibir_feedback_questao(q, q_est)
    st.divider()


def _formatar_data_hora(iso_str: str | None) -> str:
    """Formata timestamp ISO do SQLite para exibição legível."""
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.astimezone().strftime("%d/%m/%Y %H:%M:%S")
    except ValueError:
        return iso_str


def renderizar_historico(
    geracao_id: str,
    usuario_id: str,
    key_prefix: str = "quiz",
) -> None:
    """Exibe histórico persistido no SQLite via `GET /quiz/{geracao_id}/historico`."""
    estado = st.session_state["quiz"][geracao_id]

    col_tit, col_btn = st.columns([3, 1])
    col_tit.markdown("### 📊 Histórico de Tentativas (SQLite)")
    if col_btn.button("🔄 Atualizar histórico", key=f"btn_hist_{key_prefix}_{geracao_id}", use_container_width=True):
        estado["historico"] = None

    if estado.get("historico") is None:
        try:
            estado["historico"] = api_client.obter_historico(geracao_id, usuario_id)
        except ApiError as err:
            st.error(f"❌ Não foi possível carregar o histórico: {err.mensagem_amigavel}")
            return

    registros = estado.get("historico") or []
    if not registros:
        st.info("Nenhuma tentativa registrada ainda para este Quiz.")
        return

    linhas_tabela: list[dict[str, Any]] = []
    resumo_rodadas: dict[str, dict[str, int]] = {}
    resumo_assuntos: dict[str, dict[str, int]] = {}

    for r in registros:
        rid_full = str(r.get("rodada_id", ""))
        rid_curto = rid_full[:8] if rid_full else "—"
        q_idx = int(r.get("questao_indice", 0))
        alt_idx = int(r.get("alternativa_escolhida", 0))
        acertou = bool(r.get("acertou"))  # SQLite retorna 0 ou 1 no /historico
        assunto = str(r.get("assunto") or "Geral")

        linhas_tabela.append(
            {
                "Data/Hora": _formatar_data_hora(r.get("data_hora")),
                "Rodada": rid_curto,
                "Questão": q_idx + 1,
                "Tentativa": int(r.get("tentativa_numero", 1)),
                "Alternativa": _letra_alternativa(alt_idx),
                "Resultado": "✅ Acerto" if acertou else "❌ Erro",
                "Assunto": assunto,
            }
        )

        rr = resumo_rodadas.setdefault(rid_curto, {"tentativas": 0, "acertos": 0})
        rr["tentativas"] += 1
        if acertou:
            rr["acertos"] += 1

        ra = resumo_assuntos.setdefault(assunto, {"Acertos": 0, "Erros": 0})
        if acertou:
            ra["Acertos"] += 1
        else:
            ra["Erros"] += 1

    st.dataframe(linhas_tabela, use_container_width=True, hide_index=True)

    c_rod, c_ass = st.columns(2)
    with c_rod:
        st.markdown("**Resumo por Rodada:**")
        st.dataframe(
            [
                {"Rodada": k, "Tentativas": v["tentativas"], "Acertos": v["acertos"]}
                for k, v in resumo_rodadas.items()
            ],
            use_container_width=True,
            hide_index=True,
        )
    with c_ass:
        st.markdown("**Desempenho por Assunto:**")
        dados_assunto = [
            {"Assunto": k, "Acertos": v["Acertos"], "Erros": v["Erros"]}
            for k, v in resumo_assuntos.items()
        ]
        st.bar_chart(dados_assunto, x="Assunto", y=["Acertos", "Erros"])


def renderizar_quiz(
    geracao_id: str,
    usuario_id: str,
    sessao_id: str,
    questoes_iniciais: list[dict[str, Any]] | None = None,
    key_prefix: str = "quiz",
) -> None:
    """Orquestra o painel completo do Quiz interativo sem gabarito antecipado."""
    try:
        estado = carregar_quiz(geracao_id, usuario_id, questoes=questoes_iniciais)
    except ApiError as err:
        st.error(f"❌ {err.mensagem_amigavel}")
        return

    questoes = estado["questoes"]
    total = len(questoes)
    if total == 0:
        st.warning("Este Quiz não possui questões disponíveis.")
        return

    rodada_id = estado.get("rodada_id")
    q_estados = estado["questoes_estado"]
    encerradas = sum(1 for e in q_estados.values() if e["encerrada"])
    acertos = sum(1 for e in q_estados.values() if any(t["acertou"] for t in e["tentativas"]))

    c_info, c_btn = st.columns([2.6, 1.4])
    if rodada_id:
        c_info.markdown(f"**Rodada ativa:** `{rodada_id[:8]}` · Encerradas: **{encerradas}/{total}** · Acertos: **{acertos}/{total}**")
        rotulo_btn = "🔄 Iniciar nova rodada"
    else:
        c_info.info("Gabarito oculto no servidor. Inicie uma rodada para responder (até 3 tentativas por questão).")
        rotulo_btn = "▶ Iniciar rodada"

    if c_btn.button(rotulo_btn, type="primary" if not rodada_id else "secondary", use_container_width=True, key=f"btn_rodada_{key_prefix}_{geracao_id}"):
        try:
            iniciar_nova_rodada(geracao_id, usuario_id, sessao_id)
            st.rerun()
        except ApiError as err:
            st.error(f"❌ Não foi possível iniciar a rodada: {err.mensagem_amigavel}")

    st.progress(encerradas / total if total else 0.0)
    if rodada_id and encerradas == total:
        st.success(f"🏁 Rodada `{rodada_id[:8]}` concluída! Placar final: **{acertos} de {total}** acertos.")

    st.divider()
    for idx in range(total):
        _renderizar_questao_fragment(geracao_id, idx, usuario_id, sessao_id, key_prefix=key_prefix)

    renderizar_historico(geracao_id, usuario_id, key_prefix=key_prefix)
