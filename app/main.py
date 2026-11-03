import csv
import io
import json
import time
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E IDIOMA
# ==============================================================================
st.set_page_config(
    page_title="NovaMente · Estúdio de Aprendizagem",
    page_icon="✿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# HACK: Forçar o idioma pt-BR no HTML raiz para evitar o popup de tradução do Chrome
components.html(
    """
    <script>
        window.parent.document.documentElement.lang = 'pt-BR';
        window.parent.document.documentElement.setAttribute("translate", "no");
    </script>
    """,
    width=0,
    height=0,
)

# ==============================================================================
# 2. TOKENS CSS & IDENTIDADE VISUAL (BRANDBOOK UX/UI)
# ==============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --color-primary: #A8E6CF;
        --color-secondary: #CDB4DB;
        --color-accent: #FFC8DD;
        --color-surface-mint: #D8F3DC;
        --color-surface-lavender: #EDE4F5;
        --color-surface-pink: #FFF0F5;
        --color-bg: #FAFAFC;
        --color-surface: #FFFFFF;
        --color-border: #F1F3F5;
        --color-text: #293241;
        --color-text-muted: #657080;
        --radius-card: 16px;
        --radius-control: 10px;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        color: var(--color-text);
        background-color: var(--color-bg);
    }

    .stApp {
        background-color: var(--color-bg);
    }

    /* Estilização da Sidebar */
    section[data-testid="stSidebar"] {
        background-color: var(--color-surface);
        border-right: 1px solid var(--color-border);
    }

    /* Botões */
    div.stButton > button[kind="primary"] {
        background-color: var(--color-primary) !important;
        color: var(--color-text) !important;
        border: 1px solid #8fd9be !important;
        border-radius: var(--radius-control) !important;
        font-weight: 700 !important;
        padding: 0.55rem 1rem !important;
        transition: all 0.2s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        filter: brightness(0.96);
        box-shadow: 0 4px 12px rgba(41, 50, 65, 0.08);
    }

    div.stButton > button[kind="secondary"] {
        background-color: var(--color-surface-lavender) !important;
        color: var(--color-text) !important;
        border: 1px solid var(--color-secondary) !important;
        border-radius: var(--radius-control) !important;
        font-weight: 600 !important;
    }

    /* Classes Customizadas */
    .nm-brand { display: flex; align-items: center; gap: 12px; font-size: 22px; font-weight: 800; color: var(--color-text); letter-spacing: -0.6px; margin-bottom: 16px; }
    .nm-logo { width: 40px; height: 40px; border-radius: 12px; background: linear-gradient(135deg, var(--color-primary), var(--color-secondary)); display: flex; align-items: center; justify-content: center; font-size: 22px; color: var(--color-text); }
    .nm-eyebrow { font-size: 12px; color: #6b50c5; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; margin-bottom: 4px; }
    .nm-hero { background: linear-gradient(112deg, #D8F3DC 0%, #EDE4F5 57%, #FFF0F5 100%); border-radius: 24px; padding: 30px 34px; border: 1px solid var(--color-border); margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between; gap: 20px; }
    .nm-hero h1 { font-size: 30px; font-weight: 800; color: var(--color-text); margin: 6px 0 10px 0; letter-spacing: -0.8px; }
    .nm-hero p { color: var(--color-text); font-size: 15px; margin: 0; max-width: 620px; line-height: 1.6; }
    .nm-hero-art { font-size: 56px; background: rgba(255, 255, 255, 0.75); width: 120px; height: 110px; display: flex; align-items: center; justify-content: center; border-radius: 26px; transform: rotate(-5deg); flex-shrink: 0; }
    .nm-card { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-card); padding: 22px; box-shadow: 0 4px 14px rgba(41, 50, 65, 0.03); margin-bottom: 16px; }
    .nm-stat-card { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-card); padding: 20px; box-shadow: 0 4px 14px rgba(41, 50, 65, 0.03); }
    .nm-stat-value { font-size: 28px; font-weight: 800; color: var(--color-text); margin: 10px 0 2px 0; }
    .nm-stat-label { font-size: 13px; color: var(--color-text-muted); }
    .nm-pill { display: inline-block; padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; color: var(--color-text); margin-right: 6px; margin-bottom: 6px; }
    .nm-pill-mint { background-color: var(--color-surface-mint); }
    .nm-pill-lavender { background-color: var(--color-surface-lavender); }
    .nm-pill-pink { background-color: var(--color-surface-pink); }
    .nm-flashcard { padding: 20px; background: linear-gradient(135deg, #F2FCF7, #F7F4FC); border: 1px solid #E2D9F3; border-radius: var(--radius-card); margin-bottom: 12px; }
    .nm-sidebar-foot { padding: 16px; background: var(--color-surface-mint); border-radius: var(--radius-card); color: var(--color-text); font-size: 12.5px; line-height: 1.5; margin-top: 20px; }
    .nm-note { padding: 13px 16px; background: #FFF9E8; border: 1px solid #F5E6B8; border-radius: 12px; color: #5C4D26; font-size: 13px; margin: 12px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# 3. INICIALIZAÇÃO DE ESTADO
# ==============================================================================
if "pagina_atual" not in st.session_state:
    st.session_state["pagina_atual"] = "Visão geral"

if "fontes" not in st.session_state:
    st.session_state["fontes"] = [
        {
            "id": "fonte-oci-vcn-01",
            "titulo": "Introdução à Arquitetura de Redes VCN na OCI",
            "conteudo": "A Virtual Cloud Network (VCN) é uma rede privada e personalizável configurada na Oracle Cloud Infrastructure. Semelhante a uma rede de data center tradicional, a VCN oferece controle total sobre seu ambiente de rede, incluindo sub-redes públicas e privadas, tabelas de roteamento, Internet Gateways, NAT Gateways e Security Lists para controle de tráfego via regras de entrada (ingress) e saída (egress).",
            "tipo": "Texto",
            "pronto": True,
            "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
    ]

if "resultados" not in st.session_state:
    st.session_state["resultados"] = []

if "resultado_ativo" not in st.session_state:
    st.session_state["resultado_ativo"] = None

# ==============================================================================
# 4. FUNÇÕES AUXILIARES E PIPELINE MOCK
# ==============================================================================
def navegar_para(pagina: str, limpar_ativo: bool = False):
    st.session_state["pagina_atual"] = pagina
    if limpar_ativo:
        st.session_state["resultado_ativo"] = None

def extrair_conceitos_chave(texto: str) -> list[str]:
    palavras_relevantes = []
    for p in texto.replace(",", " ").replace(".", " ").replace("(", " ").replace(")", " ").split():
        if len(p) >= 5 and p[0].isupper() and p not in palavras_relevantes:
            palavras_relevantes.append(p)
    return palavras_relevantes[:6] if palavras_relevantes else ["Arquitetura", "Infraestrutura", "Configuração", "Segurança"]

def executar_pipeline_novamente(payload_entrada: dict) -> dict:
    """Mock do processamento central (RAG + Agentes + OCI)"""
    titulo = payload_entrada["documento_titulo"]
    perfil = payload_entrada["perfil_destinatario"]
    formato = payload_entrada["formato_saida"]
    nicho = payload_entrada["nicho_setor"]
    detalhe = payload_entrada["nivel_detalhe"]
    
    tempo_estudo = max(3, round(len(payload_entrada["documento_conteudo"].split()) / 40) + 3)
    timestamp_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    return {
        "id": f"nm-{timestamp_id}",
        "status": "sucesso",
        "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "payload_entrada": payload_entrada,
        "metadados": {
            "perfil_aplicado": perfil,
            "formato_gerado": formato,
            "nicho_setor": nicho,
            "nivel_detalhe": detalhe,
            "tempo_estimado_estudo_minutos": tempo_estudo,
            "conceitos_chave": extrair_conceitos_chave(payload_entrada["documento_conteudo"]),
        },
        "conteudo_adaptado": {
            "titulo": f"{titulo} — Guia {formato}",
            "introducao_contextualizada": f"Material didático adaptado com linguagem acolhedora e objetiva para o perfil **{perfil}**, contextualizado para o setor **{nicho}** em nível **{detalhe}**.",
            "itens": [
                {
                    "frente": f"O que é o conceito central para o contexto {nicho}?",
                    "verso": f"Trata-se da arquitetura descrita no documento base, adaptada para o nível {perfil}.",
                    "dica_didatica": "Pense neste componente como o alicerce principal do sistema.",
                    "opcoes_quiz": ["Opção correta fundamentada no texto.", "Opção incorreta isolada.", "Alternativa fora do contexto."],
                    "indice_correto": 0,
                },
                {
                    "frente": "Como aplicar este conhecimento na prática?",
                    "verso": "Mapeando os requisitos e segmentando o ambiente conforme as regras descritas no documento de origem.",
                    "dica_didatica": "Estruture antes de executar.",
                    "opcoes_quiz": ["Acessar diretamente sem planejamento.", "Segmentar e validar requisitos antes da implementação.", "Ignorar a arquitetura base."],
                    "indice_correto": 1,
                }
            ],
        },
        "avaliacao_qualidade": {
            "ancoragem_fonte_score": 0.98,
            "clareza_pedagogica": "Alta",
            "observacoes": f"Linguagem ajustada com analogias para {perfil}, mantendo fidelidade à fonte.",
        },
        "armazenamento_oci": {
            "bucket": "novamente-conteudos-educativos",
            "objeto_id": f"conteudo-{formato.lower().split()[0]}-{timestamp_id}.json",
            "status_upload": "concluido",
        },
    }

def exportar_arquivos(res: dict):
    b1, b2, b3 = st.columns(3)
    b1.download_button("⬇️ Baixar JSON", data=json.dumps(res, ensure_ascii=False, indent=2), file_name=res["armazenamento_oci"]["objeto_id"], mime="application/json", use_container_width=True, key=f"dl_json_{res['id']}")
    
    # Gerador Markdown
    md_content = f"# {res['conteudo_adaptado']['titulo']}\n\n{res['conteudo_adaptado']['introducao_contextualizada']}\n\n## Conteúdo\n"
    for idx, item in enumerate(res['conteudo_adaptado']['itens'], 1):
        md_content += f"### {idx}. {item['frente']}\n{item['verso']}\n> 💡 Dica: {item.get('dica_didatica', '')}\n\n"
    b2.download_button("📝 Baixar Markdown", data=md_content, file_name=f"{res['id']}.md", mime="text/markdown", use_container_width=True, key=f"dl_md_{res['id']}")
    
    # Gerador CSV (Anki)
    buf = io.StringIO()
    csv.writer(buf, delimiter=";").writerows([["Frente", "Verso", "Dica"]] + [[i.get("frente", ""), i.get("verso", ""), i.get("dica_didatica", "")] for i in res["conteudo_adaptado"]["itens"]])
    b3.download_button("🗂️ Baixar CSV (Anki)", data=buf.getvalue(), file_name=f"{res['id']}_anki.csv", mime="text/csv", use_container_width=True, key=f"dl_csv_{res['id']}")

def renderizar_previa_conteudo(res: dict, prefixo_key: str):
    meta, cont, qual, oci = res["metadados"], res["conteudo_adaptado"], res["avaliacao_qualidade"], res["armazenamento_oci"]
    
    st.markdown(f"<div><span class='nm-pill nm-pill-pink'>✨ {meta['formato_gerado']}</span><span class='nm-pill nm-pill-lavender'>👤 {meta['perfil_aplicado']}</span><span class='nm-pill nm-pill-mint'>🏢 {meta['nicho_setor']}</span></div>", unsafe_allow_html=True)
    st.markdown(f"### {cont['titulo']}")
    st.write(cont["introducao_contextualizada"])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("⏱️ Tempo de Estudo", f"{meta['tempo_estimado_estudo_minutos']} min")
    m2.metric("🎯 Ancoragem RAG", f"{int(qual['ancoragem_fonte_score'] * 100)}%")
    m3.metric("🎓 Clareza", qual["clareza_pedagogica"])
    m4.metric("☁️ OCI Bucket", oci["status_upload"].upper())
    st.divider()

    itens = cont.get("itens", [])
    fmt = meta["formato_gerado"]

    if fmt == "Flashcards":
        for idx, item in enumerate(itens, 1):
            with st.expander(f"🗂️ Cartão {idx} · {item['frente']}", expanded=(idx == 1)):
                st.markdown(f"<div class='nm-flashcard'><strong>Explicação:</strong><p>{item['verso']}</p><small>💡 {item.get('dica_didatica', '')}</small></div>", unsafe_allow_html=True)
    elif fmt == "Quiz Interativo":
        for idx, item in enumerate(itens, 1):
            st.markdown(f"**{idx}. {item['frente']}**")
            escolha = st.radio("Resposta:", options=item.get("opcoes_quiz", []), index=None, key=f"{prefixo_key}_{res['id']}_{idx}", label_visibility="collapsed")
            if escolha:
                if escolha == item["opcoes_quiz"][item.get("indice_correto", 0)]:
                    st.success(f"✅ **Correto!** {item['verso']}")
                else:
                    st.error(f"❌ **Revise este ponto:** A resposta correta é: *{item['opcoes_quiz'][item.get('indice_correto', 0)]}*")
            st.markdown("---")
    else:
        for idx, item in enumerate(itens, 1):
            st.markdown(f"<div class='nm-card'><span class='nm-pill nm-pill-mint'>Etapa 0{idx}</span><h4>{item['frente']}</h4><p>{item['verso']}</p><small>💡 {item.get('dica_didatica', '')}</small></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='nm-note'>🛡️ <strong>Auditoria de Fidelidade:</strong> {qual['observacoes']} | <strong>Bucket OCI:</strong> <code>{oci['bucket']}/{oci['objeto_id']}</code></div>", unsafe_allow_html=True)

# ==============================================================================
# 5. SIDEBAR DE NAVEGAÇÃO
# ==============================================================================
with st.sidebar:
    st.markdown("<div class='nm-brand'><div class='nm-logo'>✿</div><div>NovaMente</div></div>", unsafe_allow_html=True)
    st.caption("MENU PRINCIPAL")

    for nome, icone in {"Visão geral": "◫ Visão geral", "Minha biblioteca": "▤ Minha biblioteca", "Estúdio de criação": "✧ Estúdio de criação", "Meus conteúdos": "▣ Meus conteúdos"}.items():
        if st.button(icone, use_container_width=True, type="primary" if st.session_state["pagina_atual"] == nome else "secondary"):
            navegar_para(nome, limpar_ativo=(nome != "Estúdio de criação"))
            st.rerun()

    st.markdown("<div class='nm-sidebar-foot'><strong>🌱 Aprender é florescer</strong><p style='margin-top:6px;'>Transforme conhecimento técnico em experiências de aprendizagem com clareza, leveza e autonomia.</p></div>", unsafe_allow_html=True)
    st.caption("☁️ OCI Object Storage · Always Free")

st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center;'><span style='color:#657080; font-size:14px;'>Espaço de aprendizagem / **{st.session_state['pagina_atual']}**</span><span class='nm-pill nm-pill-lavender'>✦ Hackathon ONE G10</span></div>", unsafe_allow_html=True)

# ==============================================================================
# ROTEAMENTO DAS PÁGINAS
# ==============================================================================
pagina = st.session_state["pagina_atual"]

if pagina == "Visão geral":
    st.markdown("<div class='nm-hero'><div><div class='nm-eyebrow'>SEU ESPAÇO DE APRENDIZAGEM ✦</div><h1>Ideias complexas, aprendizado mais leve.</h1><p>Transforme documentos técnicos densos em experiências de estudo personalizadas, ancoradas nas fontes originais via RAG e armazenadas na Oracle Cloud (OCI).</p></div><div class='nm-hero-art'>📚✨</div></div>", unsafe_allow_html=True)
    
    c1, c2, _ = st.columns([1.2, 1.2, 2.6])
    if c1.button("✦ Criar conteúdo educativo →", type="primary", use_container_width=True): navegar_para("Estúdio de criação"), st.rerun()
    if c2.button("📂 Gerenciar biblioteca", type="secondary", use_container_width=True): navegar_para("Minha biblioteca"), st.rerun()
    st.write("")

    s1, s2, s3, s4 = st.columns(4)
    s1.markdown(f"<div class='nm-stat-card'><h3>📂</h3><div class='nm-stat-value'>{len(st.session_state['fontes'])}</div><div class='nm-stat-label'>Fontes adicionadas</div></div>", unsafe_allow_html=True)
    s2.markdown(f"<div class='nm-stat-card'><h3>✨</h3><div class='nm-stat-value'>{len(st.session_state['resultados'])}</div><div class='nm-stat-label'>Conteúdos criados</div></div>", unsafe_allow_html=True)
    s3.markdown(f"<div class='nm-stat-card'><h3>🎯</h3><div class='nm-stat-value'>{len(set(r['metadados']['formato_gerado'] for r in st.session_state['resultados']))}</div><div class='nm-stat-label'>Formatos explorados</div></div>", unsafe_allow_html=True)
    s4.markdown("<div class='nm-stat-card'><h3>☁️</h3><div class='nm-stat-value'>OCI Free</div><div class='nm-stat-label'>Object Storage</div></div>", unsafe_allow_html=True)

    c_rec, c_steps = st.columns([1.35, 1])
    with c_rec:
        st.markdown("<div class='nm-card'><h3>🌷 Seus conteúdos recentes</h3>", unsafe_allow_html=True)
        if not st.session_state["resultados"]: st.info("🌱 Seus primeiros conteúdos aparecerão aqui.")
        for r in st.session_state["resultados"][:3]:
            rc1, rc2 = st.columns([3, 1])
            rc1.markdown(f"**{r['conteudo_adaptado']['titulo']}**\n\n<small>{r['metadados']['formato_gerado']} · {r['criado_em']}</small>", unsafe_allow_html=True)
            if rc2.button("Abrir", key=f"dash_{r['id']}", use_container_width=True):
                st.session_state["resultado_ativo"] = r
                navegar_para("Estúdio de criação"), st.rerun()
            st.divider()
        st.markdown("</div>", unsafe_allow_html=True)
    with c_steps:
        st.markdown("<div class='nm-card'><h3>Seu próximo passo 🌸</h3><p><strong>01 · Fontes:</strong> Importar PDF/Texto <span class='nm-pill nm-pill-mint'>Biblioteca</span><br><strong>02 · Personalizar:</strong> Definir perfil/formato <span class='nm-pill nm-pill-lavender'>Estúdio</span><br><strong>03 · Gerar:</strong> Processar (IA+RAG) <span class='nm-pill nm-pill-pink'>Pipeline</span><br><strong>04 · Aprender:</strong> Estudar e exportar <span class='nm-pill nm-pill-mint'>OCI</span></p></div>", unsafe_allow_html=True)

elif pagina == "Minha biblioteca":
    st.markdown("<div class='nm-eyebrow'>ORGANIZE SEU CONHECIMENTO</div>", unsafe_allow_html=True)
    st.title("Minha biblioteca 📂")
    c_add, c_list = st.columns([1.15, 1])
    
    with c_add:
        st.markdown("<div class='nm-card'><h3>➕ Adicionar material</h3>", unsafe_allow_html=True)
        arquivos = st.file_uploader("Selecione arquivos (.pdf, .md, .txt)", accept_multiple_files=True)
        if arquivos and st.button("📥 Salvar arquivos", type="primary", use_container_width=True):
            for arq in arquivos:
                st.session_state["fontes"].insert(0, {"id": f"src-{datetime.now().timestamp()}", "titulo": arq.name, "conteudo": f"Conteúdo processado de {arq.name}", "tipo": arq.name.split('.')[-1].upper(), "pronto": True, "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M")})
            st.success("✅ Arquivos salvos!"), st.rerun()
        st.divider()
        t_man = st.text_input("Título do material")
        c_man = st.text_area("Conteúdo da documentação", height=120)
        if st.button("+ Adicionar texto", type="primary", use_container_width=True) and t_man and c_man:
            st.session_state["fontes"].insert(0, {"id": f"src-{datetime.now().timestamp()}", "titulo": t_man, "conteudo": c_man, "tipo": "Texto", "pronto": True, "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M")})
            st.success("✅ Fonte adicionada!"), st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with c_list:
        st.markdown(f"<div class='nm-card'><h3>📚 Materiais ({len(st.session_state['fontes'])})</h3>", unsafe_allow_html=True)
        for idx, f in enumerate(st.session_state["fontes"]):
            fc1, fc2 = st.columns([3.5, 1])
            fc1.markdown(f"📄 **{f['titulo']}**\n\n<small>{f['tipo']} · {f['criado_em']}</small>", unsafe_allow_html=True)
            if fc2.button("Excluir", key=f"del_{f['id']}", use_container_width=True):
                st.session_state["fontes"].pop(idx)
                st.rerun()
            st.divider()
        st.markdown("</div>", unsafe_allow_html=True)

elif pagina == "Estúdio de criação":
    st.markdown("<div class='nm-eyebrow'>SEU ESTÚDIO CRIATIVO</div>", unsafe_allow_html=True)
    st.title("Crie uma nova experiência ✨")
    cf, cp = st.columns([0.92, 1.08], gap="large")

    with cf:
        st.markdown("<div class='nm-card'><h3>01 · Personalização</h3>", unsafe_allow_html=True)
        fontes_dict = {f["titulo"]: f for f in st.session_state["fontes"]}
        fonte_sel = st.selectbox("Material de origem", options=list(fontes_dict.keys())) if fontes_dict else None
        
        p1, p2 = st.columns(2)
        perfil = p1.selectbox("Perfil do destinatário", ["Iniciante / Transição", "Júnior / Pleno", "Líder Técnico / Arquiteto", "Gestor / Executivo"])
        nicho = p2.selectbox("Contexto (Nicho)", ["Geral", "Fintech", "Saúde", "E-commerce"])
        detalhe = st.select_slider("Nível de detalhe", ["Sintético", "Didático", "Aprofundado"], "Didático")
        
        st.subheader("02 · Formato pedagógico")
        formato = st.radio("Formato", ["Flashcards", "Quiz Interativo", "Guia Prático Passo a Passo (Tutorial)", "Resumo Executivo (TL;DR)", "Roteiro de Aula / Vídeo"], horizontal=True)
        st.markdown("<div class='nm-note'>🔎 <strong>Pipeline:</strong> Extração RAG + IA Generativa + OCI Storage.</div>", unsafe_allow_html=True)

        if st.button("✦ Gerar conteúdo educacional", type="primary", use_container_width=True):
            if not fonte_sel: st.error("❌ Selecione uma fonte.")
            else:
                with st.status("Processando pipeline educacional...", expanded=True) as status:
                    st.write("🔍 Extraindo e segmentando texto do documento...")
                    time.sleep(1)
                    st.write("🧠 Executando busca vetorial (RAG)...")
                    time.sleep(1)
                    st.write("✨ Gerando adaptação pedagógica com LLM...")
                    novo_res = executar_pipeline_novamente({
                        "documento_titulo": fonte_sel,
                        "documento_conteudo": fontes_dict[fonte_sel]["conteudo"],
                        "perfil_destinatario": perfil,
                        "formato_saida": formato,
                        "nicho_setor": nicho,
                        "nivel_detalhe": detalhe
                    })
                    st.write("☁️ Salvando artefatos no OCI Object Storage...")
                    time.sleep(0.5)
                    status.update(label="Conteúdo gerado e persistido com sucesso!", state="complete", expanded=False)
                
                st.session_state["resultados"].insert(0, novo_res)
                st.session_state["resultado_ativo"] = novo_res
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with cp:
        st.markdown("<div class='nm-card'><h3>03 · Prévia do conteúdo</h3>", unsafe_allow_html=True)
        res_ativo = st.session_state.get("resultado_ativo")
        if not res_ativo and st.session_state["resultados"]: res_ativo = st.session_state["resultados"][0]
        
        if res_ativo:
            renderizar_previa_conteudo(res_ativo, "previa_studio")
            exportar_arquivos(res_ativo)
        else:
            st.markdown("<div style='text-align:center; padding:60px; color:#657080;'><h1 style='font-size:50px;'>🪄</h1><h3>Seu conteúdo aparece aqui</h3></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif pagina == "Meus conteúdos":
    st.markdown("<div class='nm-eyebrow'>SEU ACERVO DE APRENDIZAGEM</div>", unsafe_allow_html=True)
    st.title("Meus conteúdos 🌷")
    if not st.session_state["resultados"]: st.info("🗂️ Nenhum conteúdo gerado ainda.")
    
    for item in st.session_state["resultados"]:
        with st.expander(f"✨ {item['conteudo_adaptado']['titulo']} | {item['metadados']['perfil_aplicado']} ({item['criado_em']})"):
            t1, t2, t3 = st.tabs(["📖 Estudar", "🧾 JSON", "☁️ OCI & Downloads"])
            with t1: renderizar_previa_conteudo(item, f"hist_{item['id']}")
            with t2:
                c_in, c_out = st.columns(2)
                c_in.markdown("**📥 Payload de Entrada:**")
                c_in.json(item["payload_entrada"])
                c_out.markdown("**📤 Payload de Saída:**")
                c_out.json({k: v for k, v in item.items() if k not in ["id", "criado_em", "payload_entrada"]})
            with t3:
                st.markdown(f"#### ☁️ OCI Object Storage\n- **Bucket:** `{item['armazenamento_oci']['bucket']}`\n- **Objeto ID:** `{item['armazenamento_oci']['objeto_id']}`\n- **Status:** `{item['armazenamento_oci']['status_upload']}`")
                exportar_arquivos(item)