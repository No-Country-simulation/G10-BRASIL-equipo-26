"""Renderizadores dos formatos não-Quiz, fontes RAG, cabeçalho e exportações."""

import csv
import html
import io
import json
from datetime import datetime
from typing import Any

import streamlit as st

from oci_bridge import montar_pacote_artefato, rotulo_status_oci


def _esc(valor: Any) -> str:
    """Escapa texto para uso seguro dentro de blocos HTML customizados."""
    return html.escape(str(valor if valor is not None else ""))


def renderizar_fontes(fontes: list[dict[str, Any]] | None) -> None:
    """Exibe todas as referências de páginas e chunk_ids associadas a um item."""
    if not fontes:
        return

    badges: list[str] = []
    for f in fontes:
        paginas = f.get("paginas") or []
        chunks = f.get("chunk_ids") or []
        pags_str = ", ".join(str(p) for p in paginas) if paginas else "—"
        if chunks:
            chunks_str = ", ".join(f"<code>{_esc(c)}</code>" for c in chunks)
            badges.append(f"📄 Pág(s): {_esc(pags_str)} | Chunks: {chunks_str}")
        else:
            badges.append(f"📄 Pág(s): {_esc(pags_str)}")

    st.markdown(
        "<div>"
        + " ".join(f"<span class='nm-badge-source'>{b}</span>" for b in badges)
        + "</div>",
        unsafe_allow_html=True,
    )


def renderizar_cabecalho_resultado(res: dict[str, Any]) -> None:
    """Exibe badges de perfil/nível/formato, métricas reais da API e aviso de adequação."""
    fmt = res.get("formato", "Conteúdo")
    perfil = res.get("perfil", "—")
    nivel = res.get("nivel", "—")
    duracao_ms = res.get("duracao_ms")
    duracao_s = f"{duracao_ms / 1000:.1f} s" if isinstance(duracao_ms, (int, float)) else "—"

    if fmt == "Quiz":
        qtd = len(res.get("questoes") or [])
    else:
        cont = res.get("conteudo") or {}
        qtd = (
            len(cont.get("passos") or [])
            or len(cont.get("itens") or [])
            or len(cont.get("etapas") or [])
            or len(cont.get("secoes") or [])
            or len(cont.get("pontos_chave") or [])
            or res.get("quantidade_itens", 0)
        )

    oci_info = res.get("armazenamento_oci")
    badge_oci, desc_oci = rotulo_status_oci(oci_info)

    st.markdown(
        f"<div>"
        f"<span class='nm-pill nm-pill-pink'>✨ Formato: {_esc(fmt)}</span>"
        f"<span class='nm-pill nm-pill-lavender'>👤 Perfil: {_esc(perfil)}</span>"
        f"<span class='nm-pill nm-pill-mint'>🎯 Nível: {_esc(nivel)}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("⏱️ Duração API", duracao_s)
    m2.metric("📦 Itens", str(qtd))
    m3.metric("🆔 Geração", str(res.get("id", ""))[:8] or "—")
    m4.metric("☁️ Persistência", badge_oci)

    adequacao = res.get("adequacao") or {}
    if adequacao.get("divergencia") and adequacao.get("mensagem"):
        st.warning(f"⚠️ **Adequação pedagógica:** {adequacao['mensagem']}")

    st.caption(
        f"Documento: **{res.get('documento_nome', '—')}** · "
        f"Avaliação ID: `{res.get('avaliacao_id') or '—'}` · {desc_oci}"
    )
    st.divider()


def renderizar_conteudo_nao_quiz(res: dict[str, Any]) -> None:
    """Renderiza Tutorial, Flashcards, TL;DR, Roteiro e Resumo segundo o contrato v0.3."""
    fmt = res.get("formato", "")
    cont = res.get("conteudo") or {}

    if fmt == "Tutorial":
        if cont.get("titulo"):
            st.markdown(f"### {cont['titulo']}")
        for idx, p in enumerate(cont.get("passos", []), 1):
            dica_html = (
                f"<br><small>💡 <strong>Dica:</strong> {_esc(p['dica_didatica'])}</small>"
                if p.get("dica_didatica")
                else ""
            )
            st.markdown(
                f"<div class='nm-step-card'>"
                f"<span class='nm-pill nm-pill-mint'>Passo {idx:02d}</span>"
                f"<h3 style='margin-top: 8px; font-size: 1.1rem; color: var(--color-text);'>{_esc(p.get('titulo'))}</h3>"
                f"<p style='color: var(--color-text); line-height: 1.6; margin-bottom: 0;'>{_esc(p.get('explicacao'))}</p>"
                f"{dica_html}"
                f"</div>",
                unsafe_allow_html=True,
            )
            renderizar_fontes(p.get("fontes"))

    elif fmt == "Flashcards":
        for idx, item in enumerate(cont.get("itens", []), 1):
            cls = item.get("classificacao") or {}
            assunto = cls.get("assunto")
            sub = cls.get("subassunto")
            niv = cls.get("nivel_dificuldade")
            titulo_exp = f"🗂️ Cartão {idx}: {item.get('pergunta', '')}"
            with st.expander(titulo_exp, expanded=(idx == 1)):
                pills = ""
                if assunto:
                    pills += f"<span class='nm-pill nm-pill-lavender'>{_esc(assunto)}</span>"
                if sub:
                    pills += f"<span class='nm-pill nm-pill-mint'>{_esc(sub)}</span>"
                if niv:
                    pills += f"<span class='nm-pill nm-pill-pink'>{_esc(niv)}</span>"

                st.markdown(
                    f"<div class='nm-flashcard'>"
                    f"{pills}"
                    f"<p style='font-size: 16px; font-weight: 700; color: var(--color-text); margin-top: 8px;'>{_esc(item.get('pergunta'))}</p>"
                    f"<hr style='border: 0; border-top: 1px dashed var(--color-secondary); margin: 10px 0;'>"
                    f"<strong style='color: var(--color-text);'>Resposta:</strong>"
                    f"<p style='color: var(--color-text); line-height: 1.5; margin-bottom: 0;'>{_esc(item.get('resposta'))}</p>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                renderizar_fontes(item.get("fontes"))

    elif fmt == "TL;DR":
        st.markdown(
            f"<div class='nm-tldr-box'>"
            f"<h3 style='font-size: 1.15rem; margin-top: 0; color: var(--color-text);'>📌 Síntese Executiva</h3>"
            f"<p style='font-size: 15px; line-height: 1.6; color: var(--color-text); margin-bottom: 0;'>{_esc(cont.get('resumo', ''))}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
        pontos = cont.get("pontos_chave", [])
        if pontos:
            st.markdown("### 🔑 Pontos-chave:")
            for ponto in pontos:
                st.markdown(f"- ✦ **{ponto}**")
        renderizar_fontes(cont.get("fontes"))

    elif fmt == "Roteiro":
        etapas = cont.get("etapas", [])
        duracao_total = sum(int(e.get("duracao_minutos", 0)) for e in etapas)
        st.info(f"⏱️ Duração total estimada do roteiro: **{duracao_total} minutos** ({len(etapas)} etapas)")
        for idx, et in enumerate(etapas, 1):
            st.markdown(
                f"<div class='nm-card' style='display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap;'>"
                f"<div style='color: var(--color-text);'><strong>{idx}. {_esc(et.get('atividade'))}</strong></div>"
                f"<div><span class='nm-pill nm-pill-lavender'>⏱️ {_esc(et.get('duracao_minutos', 0))} min</span></div>"
                f"</div>",
                unsafe_allow_html=True,
            )
            renderizar_fontes(et.get("fontes"))

    elif fmt == "Resumo":
        if cont.get("titulo"):
            st.markdown(f"### {cont['titulo']}")
        for sec in cont.get("secoes", []):
            st.markdown(
                f"<div class='nm-card'>"
                f"<h3 style='font-size: 1.1rem; margin-top: 0; color: var(--color-text);'>{_esc(sec.get('titulo'))}</h3>"
                f"<p style='color: var(--color-text); line-height: 1.6; margin-bottom: 0;'>{_esc(sec.get('texto'))}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )
            renderizar_fontes(sec.get("fontes"))

    else:
        st.json(cont)


def _formatar_markdown(res: dict[str, Any], estado_quiz: dict[str, Any] | None = None) -> str:
    """Gera representação Markdown respeitando o schema v0.3 e sem vazar gabarito não revelado."""
    fmt = res.get("formato", "Conteúdo")
    cont = res.get("conteudo") or {}
    titulo = cont.get("titulo") or f"{fmt} — {res.get('documento_nome', 'MentorIA Tech')}"

    linhas = [
        f"# {titulo}",
        "",
        f"> **Perfil:** {res.get('perfil')} | **Nível:** {res.get('nivel')} | **Geração ID:** `{res.get('id')}`",
        "",
        "---",
        "",
    ]

    if fmt == "Tutorial":
        for idx, p in enumerate(cont.get("passos", []), 1):
            linhas.append(f"## {idx}. {p.get('titulo', '')}")
            linhas.append(p.get("explicacao", ""))
            linhas.append("")
    elif fmt == "Flashcards":
        for idx, it in enumerate(cont.get("itens", []), 1):
            linhas.append(f"### Cartão {idx}: {it.get('pergunta', '')}")
            linhas.append(f"**Resposta:** {it.get('resposta', '')}")
            linhas.append("")
    elif fmt == "TL;DR":
        linhas.append("## Síntese Executiva")
        linhas.append(cont.get("resumo", ""))
        linhas.append("")
        linhas.append("### Pontos-chave")
        for ponto in cont.get("pontos_chave", []):
            linhas.append(f"- {ponto}")
        linhas.append("")
    elif fmt == "Roteiro":
        for idx, et in enumerate(cont.get("etapas", []), 1):
            linhas.append(f"### {idx}. {et.get('atividade', '')} ({et.get('duracao_minutos', 0)} min)")
            linhas.append("")
    elif fmt == "Resumo":
        for sec in cont.get("secoes", []):
            linhas.append(f"## {sec.get('titulo', '')}")
            linhas.append(sec.get("texto", ""))
            linhas.append("")
    elif fmt == "Quiz":
        q_estados = (estado_quiz or {}).get("questoes_estado", {})
        for idx, q in enumerate(res.get("questoes") or []):
            linhas.append(f"### Questão {idx + 1}: {q.get('enunciado', '')}")
            alts = q.get("alternativas") or []
            for j, alt in enumerate(alts):
                linhas.append(f"- {chr(65 + j)}) {alt}")
            est = q_estados.get(idx) or {}
            if est.get("encerrada") and est.get("indice_correto") is not None:
                c_idx = est["indice_correto"]
                letra = chr(65 + c_idx) if 0 <= c_idx < len(alts) else str(c_idx)
                linhas.append(f"\n> **Gabarito revelado:** {letra}) {alts[c_idx] if 0 <= c_idx < len(alts) else ''}")
                if est.get("explicacao"):
                    linhas.append(f"> **Explicação:** {est['explicacao']}")
            linhas.append("")

    linhas.append("---")
    linhas.append("*Gerado por MentorIA-Tech · Hackathon ONE G10 (Alura & Oracle)*")
    return "\n".join(linhas)


def _formatar_csv_anki(res: dict[str, Any], estado_quiz: dict[str, Any] | None = None) -> str:
    """Gera CSV separado por `;` para importação no Anki sem vazar gabarito não revelado."""
    fmt = res.get("formato", "")
    cont = res.get("conteudo") or {}
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";")

    if fmt == "Flashcards":
        writer.writerow(["Frente", "Verso", "Assunto"])
        for it in cont.get("itens", []):
            assunto = (it.get("classificacao") or {}).get("assunto", "")
            writer.writerow([it.get("pergunta", ""), it.get("resposta", ""), assunto])
    elif fmt == "Quiz":
        writer.writerow(["Pergunta", "Alternativas", "Gabarito (se revelado)"])
        q_estados = (estado_quiz or {}).get("questoes_estado", {})
        for idx, q in enumerate(res.get("questoes") or []):
            alts = q.get("alternativas") or []
            alts_txt = " | ".join(f"{chr(65 + j)}) {a}" for j, a in enumerate(alts))
            est = q_estados.get(idx) or {}
            gabarito = ""
            if est.get("encerrada") and est.get("indice_correto") is not None:
                c_idx = est["indice_correto"]
                if 0 <= c_idx < len(alts):
                    gabarito = f"{chr(65 + c_idx)}) {alts[c_idx]} — {est.get('explicacao', '')}"
            writer.writerow([q.get("enunciado", ""), alts_txt, gabarito])
    elif fmt == "Tutorial":
        writer.writerow(["Passo", "Explicação", "Formato"])
        for p in cont.get("passos", []):
            writer.writerow([p.get("titulo", ""), p.get("explicacao", ""), "Tutorial"])
    elif fmt == "Resumo":
        writer.writerow(["Seção", "Conteúdo", "Formato"])
        for sec in cont.get("secoes", []):
            writer.writerow([sec.get("titulo", ""), sec.get("texto", ""), "Resumo"])
    elif fmt == "Roteiro":
        writer.writerow(["Atividade", "Duração (min)", "Formato"])
        for et in cont.get("etapas", []):
            writer.writerow([et.get("atividade", ""), et.get("duracao_minutos", 0), "Roteiro"])
    elif fmt == "TL;DR":
        writer.writerow(["Tópico", "Conteúdo", "Formato"])
        writer.writerow(["Síntese Executiva", cont.get("resumo", ""), "TL;DR"])
        for i, pt in enumerate(cont.get("pontos_chave", []), 1):
            writer.writerow([f"Ponto-chave {i}", pt, "TL;DR"])

    return buf.getvalue()


def exportar_arquivos(
    res: dict[str, Any],
    prefixo_key: str,
    estado_quiz: dict[str, Any] | None = None,
) -> None:
    """Renderiza botões de download em JSON, Markdown e CSV (Anki)."""
    gid = str(res.get("id", "sem_id"))
    fmt_slug = str(res.get("formato", "conteudo")).lower().replace(";", "").replace(" ", "_")
    nome_base = f"mentoria_tech_{fmt_slug}_{gid[:8]}"
    pacote_json = json.dumps(montar_pacote_artefato(res), ensure_ascii=False, indent=2)

    b1, b2, b3 = st.columns(3)
    b1.download_button(
        "⬇️ Baixar JSON",
        data=pacote_json,
        file_name=f"{nome_base}.json",
        mime="application/json",
        use_container_width=True,
        key=f"dl_json_{prefixo_key}_{gid}",
    )
    b2.download_button(
        "📝 Baixar Markdown",
        data=_formatar_markdown(res, estado_quiz=estado_quiz),
        file_name=f"{nome_base}.md",
        mime="text/markdown",
        use_container_width=True,
        key=f"dl_md_{prefixo_key}_{gid}",
    )
    b3.download_button(
        "🗂️ Baixar CSV (Anki)",
        data=_formatar_csv_anki(res, estado_quiz=estado_quiz),
        file_name=f"{nome_base}_anki.csv",
        mime="text/csv",
        use_container_width=True,
        key=f"dl_csv_{prefixo_key}_{gid}",
    )


def renderizar_bloco_feedback(res: dict[str, Any], prefixo_key: str) -> None:
    """Renderiza avaliação qualitativa local da sessão dentro de `st.container(border=True)`."""
    gid = str(res.get("id", "sem_id"))
    with st.container(border=True):
        st.markdown(
            "<h3 style='font-size: 1.05rem; margin: 0 0 4px 0; color: var(--color-text);'>"
            "⭐ Avaliação do Conteúdo (Feedback local da sessão)</h3>"
            "<p style='font-size: 13px; color: var(--color-text-muted); margin-bottom: 10px;'>"
            "Registre sua percepção didática durante a demonstração (armazenado apenas na sessão atual).</p>",
            unsafe_allow_html=True,
        )
        fb_col1, fb_col2 = st.columns([1.2, 2.8])
        with fb_col1:
            nota_fb = st.feedback("stars", key=f"fb_stars_{prefixo_key}_{gid}")
        with fb_col2:
            comentario_fb = st.text_input(
                "Comentário (opcional):",
                placeholder="Ex: Linguagem muito clara e exemplos precisos.",
                key=f"fb_comm_{prefixo_key}_{gid}",
            )

        if st.button("Enviar Avaliação", key=f"btn_fb_{prefixo_key}_{gid}", type="secondary"):
            if nota_fb is not None:
                st.session_state.setdefault("feedbacks", []).append(
                    {
                        "id_conteudo": gid,
                        "estrelas": nota_fb + 1,
                        "comentario": comentario_fb,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                st.success("✅ Obrigado! Avaliação registrada localmente nesta sessão.")
            else:
                st.info("Por favor, selecione uma nota de 1 a 5 estrelas antes de enviar.")
