"""Gerenciamento de identificadores anônimos (`usuario_id` e `sessao_id`) e metadados DOM no Streamlit."""

import json
import uuid

import streamlit as st
import streamlit.components.v1 as components


def validar_uuid(valor: str | None) -> str | None:
    """Valida se a string representa um UUID válido e retorna sua forma canônica."""
    if not valor or not isinstance(valor, str):
        return None
    try:
        return str(uuid.UUID(valor.strip()))
    except (ValueError, AttributeError):
        return None


def obter_usuario_id() -> str:
    """Obtém ou cria `usuario_id` mantendo-o no `session_state` e em `?uid=` da URL."""
    atual = validar_uuid(st.session_state.get("usuario_id"))
    if atual:
        if st.query_params.get("uid") != atual:
            st.query_params["uid"] = atual
        return atual

    uid_url = validar_uuid(st.query_params.get("uid"))
    if uid_url:
        st.session_state["usuario_id"] = uid_url
        st.session_state["_uid_veio_da_url"] = True
        return uid_url

    novo_uid = str(uuid.uuid4())
    st.session_state["usuario_id"] = novo_uid
    st.session_state["_uid_veio_da_url"] = False
    st.query_params["uid"] = novo_uid
    return novo_uid


def obter_sessao_id() -> str:
    """Obtém ou cria `sessao_id` exclusivo da sessão atual do Streamlit."""
    atual = validar_uuid(st.session_state.get("sessao_id"))
    if atual:
        return atual

    novo_sid = str(uuid.uuid4())
    st.session_state["sessao_id"] = novo_sid
    return novo_sid


def sincronizar_storage_navegador(usuario_id: str, sessao_id: str) -> None:
    """
    Configura idioma `pt-BR`, bloqueio `notranslate`, meta description SEO no documento pai
    e sincroniza `novamente_usuario_id` (`localStorage`) e `novamente_sessao_id` (`sessionStorage`).
    """
    forcar_gravacao = bool(st.session_state.pop("_forcar_gravar_localstorage", False))
    veio_da_url = bool(st.session_state.get("_uid_veio_da_url", False))
    ja_verificou = bool(st.session_state.get("_localstorage_verificado", False))
    deve_restaurar_se_existir = (not veio_da_url) and (not ja_verificou) and (not forcar_gravacao)
    st.session_state["_localstorage_verificado"] = True

    uid_js = json.dumps(usuario_id)
    sid_js = json.dumps(sessao_id)
    restaurar_js = "true" if deve_restaurar_se_existir else "false"
    forcar_js = "true" if forcar_gravacao else "false"

    components.html(
        f"""
        <script>
        (function() {{
            try {{
                const doc = window.parent.document;
                const htmlEl = doc.documentElement;
                htmlEl.setAttribute('lang', 'pt-BR');
                htmlEl.setAttribute('xml:lang', 'pt-BR');
                htmlEl.setAttribute('translate', 'no');
                htmlEl.classList.add('notranslate');

                if (doc.body) {{
                    doc.body.setAttribute('translate', 'no');
                    doc.body.classList.add('notranslate');
                }}

                function garantirMeta(seletor, atributos) {{
                    if (!doc.head) return;
                    let meta = doc.head.querySelector(seletor);
                    if (!meta) {{
                        meta = doc.createElement('meta');
                        doc.head.appendChild(meta);
                    }}
                    Object.entries(atributos).forEach(([k, v]) => meta.setAttribute(k, v));
                }}

                garantirMeta('meta[name="google"]', {{
                    name: 'google',
                    content: 'notranslate'
                }});
                garantirMeta('meta[http-equiv="Content-Language"]', {{
                    'http-equiv': 'Content-Language',
                    content: 'pt-BR'
                }});
                garantirMeta('meta[name="description"]', {{
                    name: 'description',
                    content: 'MentorIA-Tech: Estúdio inteligente de adaptação de documentações técnicas em experiências de aprendizagem via RAG, IA Generativa e Oracle Cloud (OCI).'
                }});

                // Pré-conexão com o Google Fonts (Inter): antecipa DNS + TCP + TLS
                // para reduzir o atraso de renderização do texto (LCP).
                function garantirPreconnect(href, crossorigin) {{
                    if (!doc.head) return;
                    const seletor = 'link[rel="preconnect"][href="' + href + '"]';
                    if (doc.head.querySelector(seletor)) return;
                    const link = doc.createElement('link');
                    link.rel = 'preconnect';
                    link.href = href;
                    if (crossorigin) link.crossOrigin = 'anonymous';
                    doc.head.insertBefore(link, doc.head.firstChild);
                }}
                garantirPreconnect('https://fonts.googleapis.com', false);
                garantirPreconnect('https://fonts.gstatic.com', true);

                const uid = {uid_js};
                const sid = {sid_js};
                const restaurar = {restaurar_js};
                const forcar = {forcar_js};
                const uuidRegex = /^[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{12}}$/i;

                window.parent.sessionStorage.setItem('novamente_sessao_id', sid);
                const salvo = window.parent.localStorage.getItem('novamente_usuario_id');

                if (forcar) {{
                    window.parent.localStorage.setItem('novamente_usuario_id', uid);
                    return;
                }}

                if (restaurar && salvo && uuidRegex.test(salvo) && salvo.toLowerCase() !== uid.toLowerCase()) {{
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set('uid', salvo);
                    window.parent.location.replace(url.toString());
                    return;
                }}

                window.parent.localStorage.setItem('novamente_usuario_id', uid);
            }} catch (e) {{
                // Ambiente sem acesso ao DOM/storage do pai (ex.: iframe restrito)
            }}
        }})();
        </script>
        """,
        width=0,
        height=0,
    )


def definir_usuario_id(novo_uid: str) -> None:
    """Atualiza o `usuario_id` ativo, invalida caches dependentes e atualiza URL/localStorage."""
    st.session_state["usuario_id"] = novo_uid
    st.session_state["_uid_veio_da_url"] = True
    st.session_state["_forcar_gravar_localstorage"] = True
    st.session_state["quizzes_servidor"] = None
    st.session_state["quiz"] = {}
    st.query_params["uid"] = novo_uid


def renderizar_painel_identidade() -> None:
    """Renderiza painel na sidebar com os UUIDs anônimos e recuperação de ID."""
    uid = obter_usuario_id()
    sid = obter_sessao_id()

    with st.sidebar.expander("🪪 Identidade anônima", expanded=False):
        st.caption(
            "Sem login ou senha (Zero PII / LGPD): seus **Quizzes, tentativas e evolução** "
            "ficam salvos no servidor vinculados ao seu **`usuario_id`** anônimo (mantido na URL `?uid=` e no navegador). "
            "Guarde seu `usuario_id` para recuperar seu histórico em outro navegador ou dispositivo."
        )
        st.markdown("**`usuario_id` (chave anônima para recuperar seus Quizzes):**")
        st.code(uid, language=None)
        st.markdown("**`sessao_id` (identificador da visita atual):**")
        st.code(sid, language=None)

        novo_input = st.text_input(
            "Recuperar histórico com seu `usuario_id`:",
            placeholder="Cole um UUID válido e clique em Aplicar ID...",
            key="input_recuperar_uid",
        )
        col_rec, col_novo = st.columns(2)
        if col_rec.button("Aplicar ID", use_container_width=True, key="btn_aplicar_uid"):
            validado = validar_uuid(novo_input)
            if validado:
                definir_usuario_id(validado)
                st.success("ID atualizado!")
                st.rerun()
            else:
                st.error("Informe um UUID válido.")

        if col_novo.button("Novo ID", use_container_width=True, key="btn_novo_uid"):
            definir_usuario_id(str(uuid.uuid4()))
            st.rerun()

        st.caption("⚠️ Não use para dados sensíveis; limpar o navegador ou trocar a URL perde a associação.")
