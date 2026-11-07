import json
import streamlit as st

# 1. Configuração da Página
st.set_page_config(
    page_title="NovaMente | Adaptação Educacional com IA",
    page_icon="🧠",
    layout="wide",
)

# 2. Cabeçalho Principal
st.title("🧠 Projeto NovaMente")
st.subheader("Sistema Inteligente de Adaptação e Geração de Conteúdo Educacional")
st.markdown(
    "Transforme documentações técnicas densas em materiais didáticos personalizados "
    "com **RAG**, **IA Generativa** e persistência na **Oracle Cloud (OCI)**."
)
st.divider()

# 3. Sidebar: Parâmetros de Personalização (Alinhados ao Edital)
with st.sidebar:
    st.header("⚙️ Configurações do Conteúdo")

    perfil_destinatario = st.selectbox(
        "👤 Perfil do Destinatário",
        options=[
            "Iniciante / Transição de Carreira",
            "Desenvolvedor Júnior / Pleno",
            "Líder Técnico / Arquiteto",
            "Gestor / Executivo (Não Técnico)",
        ],
        help="Define a profundidade técnica, vocabulário e analogias utilizadas.",
    )

    formato_saida = st.selectbox(
        "📚 Formato Pedagógico de Saída",
        options=[
            "Flashcards",
            "Quiz Interativo",
            "Guia Prático Passo a Passo (Tutorial)",
            "Resumo Executivo (TL;DR)",
            "Roteiro de Aula / Vídeo",
        ],
        help="Estrutura didática em que o conteúdo será transformado.",
    )

    nicho_setor = st.selectbox(
        "🏢 Nicho / Contexto de Aplicação",
        options=["Geral", "Fintech", "Saúde", "E-commerce"],
        help="Adapta os exemplos práticos para o setor escolhido.",
    )

    nivel_detalhe = st.select_slider(
        "🔍 Nível de Detalhe",
        options=["Sintético", "Didático", "Aprofundado"],
        value="Didático",
    )

    st.divider()
    st.caption("☁️ **Infraestrutura:** OCI Object Storage (Always Free)")

# 4. Área Principal: Ingestão do Documento Técnico
st.markdown("### 📄 1. Fonte de Conhecimento Técnico")

documento_titulo = st.text_input(
    "Título do Documento ou Tema",
    placeholder="Ex.: Introdução à Arquitetura de Redes VCN na OCI",
)

metodo_entrada = st.radio(
    "Selecione como deseja fornecer o material técnico:",
    options=["Upload de Arquivo (PDF, Markdown, TXT)", "Inserir Texto Bruto"],
    horizontal=True,
)

documento_conteudo = ""
arquivo_upload = None

if metodo_entrada == "Upload de Arquivo (PDF, Markdown, TXT)":
    arquivo_upload = st.file_uploader(
        "Envie a documentação técnica (.pdf, .md, .txt)",
        type=["pdf", "md", "txt"],
    )
    if arquivo_upload is not None:
        st.info(f"📎 Arquivo carregado: **{arquivo_upload.name}** ({arquivo_upload.size} bytes)")
        # Leitura direta caso seja Markdown ou TXT (PDF será processado pelo módulo PyPDF no RAG)
        if arquivo_upload.name.endswith((".md", ".txt")):
            documento_conteudo = arquivo_upload.read().decode("utf-8", errors="ignore")
        else:
            documento_conteudo = f"[ Conteúdo binário do PDF: {arquivo_upload.name} ]"
else:
    documento_conteudo = st.text_area(
        "Cole aqui o conteúdo da documentação, manual ou artigo técnico:",
        height=180,
        placeholder="Ex.: A Virtual Cloud Network (VCN) é uma rede privada e personalizável configurada na Oracle Cloud Infrastructure...",
    )

# 5. Botão de Ação e Orquestração
gerar_btn = st.button("🚀 Adaptar Conteúdo Educacional", type="primary", use_container_width=True)

if gerar_btn:
    # Validação e tratamento amigável de erros
    if not documento_titulo.strip():
        st.warning("⚠️ Por favor, informe um **Título para o Documento** antes de prosseguir.")
    elif not documento_conteudo.strip() and arquivo_upload is None:
        st.error("❌ Nenhum material técnico fornecido! Faça o upload de um arquivo ou cole o texto bruto.")
    else:
        # Montagem do Payload de Entrada conforme especificação do Hackathon
        payload_entrada = {
            "documento_titulo": documento_titulo.strip(),
            "documento_conteudo": documento_conteudo.strip(),
            "perfil_destinatario": perfil_destinatario,
            "formato_saida": formato_saida,
            "nicho_setor": nicho_setor,
            "nivel_detalhe": nivel_detalhe,
        }

        with st.spinner("Processando pipeline RAG, orquestrando agentes e salvando no OCI Object Storage..."):
            # TODO: Substituir este mock pela chamada real da API (FastAPI) ou módulo RAG/Agentes
            resposta_estruturada = {
                "status": "sucesso",
                "metadados": {
                    "perfil_aplicado": perfil_destinatario,
                    "formato_gerado": formato_saida,
                    "tempo_estimado_estudo_minutos": 5,
                    "conceitos_chave": ["VCN", "Sub-redes", "Internet Gateway", "Security Lists"],
                },
                "conteudo_adaptado": {
                    "titulo": f"{documento_titulo} ({perfil_destinatario})",
                    "introducao_contextualizada": (
                        f"Conteúdo adaptado especialmente para o perfil **{perfil_destinatario}** "
                        f"aplicado ao contexto **{nicho_setor}** com nível **{nivel_detalhe}**."
                    ),
                    "itens": [
                        {
                            "frente": "O que é o conceito principal abordado no documento?",
                            "verso": "É a estrutura base descrita na documentação técnica fornecida, adaptada sem jargões excessivos.",
                            "dica_didatica": "Associe este componente à infraestrutura principal do seu projeto.",
                        },
                        {
                            "frente": "Como as regras de segurança e controle funcionam neste contexto?",
                            "verso": "Atuam como filtros inteligentes que determinam o que pode entrar (ingress) e sair (egress) do ambiente.",
                            "dica_didatica": "Pense em uma portaria com lista de permissões.",
                        },
                    ],
                },
                "avaliacao_qualidade": {
                    "ancoragem_fonte_score": 0.98,
                    "clareza_pedagogica": "Alta",
                    "observacoes": f"Linguagem ajustada com sucesso para o público {perfil_destinatario}.",
                },
                "armazenamento_oci": {
                    "bucket": "novamente-conteudos-educativos",
                    "objeto_id": f"conteudo-{formato_saida.lower().replace(' ', '-')}-001.json",
                    "status_upload": "concluido",
                },
            }

            st.session_state["ultimo_payload_entrada"] = payload_entrada
            st.session_state["ultimo_resultado"] = resposta_estruturada

# 6. Renderização dos Resultados (Se houver resultado gerado na sessão)
if "ultimo_resultado" in st.session_state:
    res = st.session_state["ultimo_resultado"]
    meta = res["metadados"]
    conteudo = res["conteudo_adaptado"]
    qualidade = res["avaliacao_qualidade"]
    oci_info = res["armazenamento_oci"]

    st.divider()
    st.markdown("### 🎯 2. Resultado da Adaptação Pedagógica")

    # Cards de Métricas (Metadados, Grounding e OCI)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("⏱️ Tempo de Estudo", f"{meta['tempo_estimado_estudo_minutos']} min")
    col2.metric("🎯 Ancoragem (RAG Score)", f"{int(qualidade['ancoragem_fonte_score'] * 100)}%")
    col3.metric("🎓 Clareza Pedagógica", qualidade["clareza_pedagogica"])
    col4.metric("☁️ Upload OCI Bucket", oci_info["status_upload"].upper())

    # Conceitos-chave extraídos
    st.markdown("**🔑 Conceitos-Chave Identificados:** " + " ".join([f"`{c}`" for c in meta["conceitos_chave"]]))

    # Abas de visualização do pacote educativo
    aba_didatica, aba_json, aba_oci = st.tabs([
        "📖 Visualização Interativa",
        "🧾 JSON Estruturado (Saída & Entrada)",
        "☁️ Persistência OCI & Exportação",
    ])

    with aba_didatica:
        st.markdown(f"#### {conteudo['titulo']}")
        st.info(conteudo["introducao_contextualizada"])

        st.markdown("##### Conteúdo Gerado:")
        for idx, item in enumerate(conteudo.get("itens", []), start=1):
            with st.expander(f"📌 Item {idx}: {item.get('frente', 'Tópico')}", expanded=True):
                st.markdown(f"**Resposta / Explicação:**\n\n{item.get('verso', '')}")
                if "dica_didatica" in item:
                    st.caption(f"💡 **Dica Didática:** {item['dica_didatica']}")

        st.success(f"📋 **Parecer do Agente Revisor:** {qualidade['observacoes']}")

    with aba_json:
        col_in, col_out = st.columns(2)
        with col_in:
            st.markdown("**📥 Payload de Requisição (Entrada):**")
            st.json(st.session_state["ultimo_payload_entrada"])
        with col_out:
            st.markdown("**📤 Payload de Resposta (Saída):**")
            st.json(res)

    with aba_oci:
        st.markdown("#### ☁️ Detalhes de Armazenamento no OCI Object Storage")
        st.write(f"- **Bucket Always Free:** `{oci_info['bucket']}`")
        st.write(f"- **Objeto ID:** `{oci_info['objeto_id']}`")
        st.write(f"- **Status:** `{oci_info['status_upload']}`")

        st.divider()
        st.markdown("#### 📥 Exportar Pacote Educacional")
        json_str = json.dumps(res, ensure_ascii=False, indent=2)
        st.download_button(
            label="⬇️ Baixar JSON Estruturado",
            data=json_str,
            file_name=oci_info["objeto_id"],
            mime="application/json",
        )