import base64
import html
import io
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image
import streamlit as st

# Garante imports locais em app/ e services/ na raiz do repositório
APP_DIR = Path(__file__).resolve().parent
REPO_DIR = APP_DIR.parent
for _p in (str(APP_DIR), str(REPO_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import api_client  # noqa: E402
from api_client import ApiError  # noqa: E402
import config  # noqa: E402
import identidade  # noqa: E402
import oci_bridge  # noqa: E402
import quiz_ui  # noqa: E402
import renderizadores  # noqa: E402


# ==============================================================================
# 1. ASSETS OTIMIZADOS (BRANDBOOK UX/UI & LIGHTHOUSE PERFORMANCE/CLS)
# ==============================================================================
def _recortar_imagem(caminho: Path, padding: int = 12) -> Image.Image | None:
    """Abre um PNG transparente e recorta as margens vazias (bounding box)."""
    if not caminho or not caminho.exists():
        return None
    try:
        img = Image.open(caminho)
        bbox = img.getbbox()
        if bbox:
            w, h = img.size
            x1 = max(0, bbox[0] - padding)
            y1 = max(0, bbox[1] - padding)
            x2 = min(w, bbox[2] + padding)
            y2 = min(h, bbox[3] + padding)
            return img.crop((x1, y1, x2, y2))
        return img.copy()
    except Exception:
        return None


@st.cache_resource(show_spinner=False)
def carregar_icone_pagina():
    """Carrega e redimensiona o favicon da aplicação."""
    img = _recortar_imagem(config.ASSETS_DIR / "Ícone principal" / "Ícone.png", padding=8)
    if img is not None:
        img.thumbnail((128, 128), Image.Resampling.LANCZOS)
    return img


@st.cache_data(show_spinner=False, ttl=86400)
def carregar_asset_otimizado_b64(
    tipo: str,
    max_size: tuple[int, int],
    display_height: int,
    padding: int = 12,
) -> tuple[str, int, int]:
    """
    Recorta, redimensiona via `Image.thumbnail` e comprime o PNG em memória (`optimize=True`).

    Retorna `(data_uri_base64, width_css, height_css)` com dimensões explícitas para zerar CLS.
    """
    mapa_caminhos = {
        "logo": config.ASSETS_DIR / "Logomarca principal" / "Logomarca principal.png",
        "logo_dark": config.REPO_DIR / "assets" / "logo-mentoria-tech-dark.png",
        "mascote": config.ASSETS_DIR / "Mascote" / "Mascote.png",
        "alura_light": config.REPO_DIR / "assets" / "logo-alura-light.png",
        "alura_dark": config.REPO_DIR / "assets" / "logo-alura-dark.png",
        "nocountry": config.REPO_DIR / "assets" / "logo-nocountry.png",
        "one_oracle": config.REPO_DIR / "assets" / "logo-one-oracle-next-education.png",
    }
    caminho = mapa_caminhos.get(tipo)
    if not caminho:
        return "", 0, 0

    img = _recortar_imagem(caminho, padding=padding)
    if img is None:
        return "", 0, 0

    try:
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        w_real, h_real = img.size
        if h_real <= 0:
            return "", 0, 0
        h_css = display_height
        w_css = max(1, round((w_real / h_real) * h_css))

        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
        return f"data:image/png;base64,{b64}", w_css, h_css
    except Exception:
        return "", 0, 0


@st.cache_resource(show_spinner=False)
def obter_http_session():
    """Mantém uma única `requests.Session` reaproveitada entre execuções."""
    return api_client.criar_session()


# show_spinner=False: o spinner padrão do cache injeta um elemento temporário no topo
# da página e desloca o layout (CLS) a cada expiração do TTL.
@st.cache_data(ttl=15, show_spinner=False)
def verificar_api_online(base_url: str) -> bool:
    """Consulta `GET /health` com cache curto de 15 segundos."""
    return api_client.verificar_saude(base_url=base_url, session=obter_http_session())


img_icone = carregar_icone_pagina()


# ==============================================================================
# 2. CONFIGURAÇÃO DA PÁGINA, IDENTIDADE E ESTADO INICIAL
# ==============================================================================
# `set_page_config` é emitido antes de qualquer outro delta para que o layout "wide"
# seja aplicado desde o primeiro paint (evita troca centered -> wide = CLS).
# `initial_sidebar_state="auto"`: expandida no desktop e recolhida no mobile, evitando
# que a sidebar de 300px comprima o conteúdo principal em telas de ~400px (CLS/LCP mobile).
st.set_page_config(
    page_title="MentorIA-Tech · Estúdio de Aprendizagem",
    page_icon=img_icone if img_icone else "🎓",
    layout="wide",
    initial_sidebar_state="auto",
)

logo_b64, logo_w, logo_h = carregar_asset_otimizado_b64("logo", max_size=(440, 160), display_height=76, padding=12)
logo_dark_b64, logo_dark_w, logo_dark_h = carregar_asset_otimizado_b64("logo_dark", max_size=(440, 160), display_height=76, padding=12)
mascote_b64, masc_w, masc_h = carregar_asset_otimizado_b64("mascote", max_size=(240, 240), display_height=116, padding=14)

if "tema" not in st.session_state:
    st.session_state["tema"] = "light"

if "pagina_atual" not in st.session_state:
    st.session_state["pagina_atual"] = "Visão geral"

if "documentos" not in st.session_state:
    st.session_state["documentos"] = []

if "resultados" not in st.session_state:
    st.session_state["resultados"] = []

if "resultado_ativo" not in st.session_state:
    st.session_state["resultado_ativo"] = None

if "quizzes_servidor" not in st.session_state:
    st.session_state["quizzes_servidor"] = None

if "quiz" not in st.session_state:
    st.session_state["quiz"] = {}

if "gerando" not in st.session_state:
    st.session_state["gerando"] = False

if "feedbacks" not in st.session_state:
    st.session_state["feedbacks"] = []

usuario_id = identidade.obter_usuario_id()
sessao_id = identidade.obter_sessao_id()
identidade.sincronizar_storage_navegador(usuario_id, sessao_id)


def alternar_tema() -> None:
    """Alterna instantaneamente entre Modo Claro e Modo Escuro."""
    st.session_state["tema"] = "dark" if st.session_state.get("tema") == "light" else "light"


# ==============================================================================
# 3. SISTEMA DE TEMAS DINÂMICO (LIGHT & DARK MODE WCAG AA) & RESPONSIVIDADE
# ==============================================================================
tema_ativo = st.session_state.get("tema", "light")

if tema_ativo == "dark":
    variaveis_tema_css = """
        --color-bg: #0F172A;
        --color-surface: #1E293B;
        --color-surface-alt: #26334D;
        --color-border: #334155;
        --color-text: #F8FAFC;
        --color-text-muted: #CBD5E1;
        --color-primary: #A8E6CF;
        --color-primary-hover: #8FD9BE;
        --color-on-primary: #0F172A;
        --color-secondary: #CDB4DB;
        --color-surface-mint: #16382C;
        --color-surface-lavender: #2E2344;
        --color-accent: #FFC8DD;
        --color-surface-pink: #3D2235;
        --color-eyebrow: #D8B4FE;
        --color-logo-box: #F8FAFC;
        --hero-gradient: linear-gradient(112deg, #132A23 0%, #241B38 55%, #331A29 100%);
        --hero-mascote-bg: rgba(30, 41, 59, 0.90);
        --flashcard-gradient: linear-gradient(135deg, #162C28 0%, #241E38 100%);
        --tldr-gradient: linear-gradient(135deg, #2D2618 0%, #331D2C 100%);
        --shadow-card: 0 6px 20px rgba(0, 0, 0, 0.35);
        color-scheme: dark;
    """
else:
    variaveis_tema_css = """
        --color-bg: #FAFAFC;
        --color-surface: #FFFFFF;
        --color-surface-alt: #F4F2F9;
        --color-border: #E5E7EB;
        --color-text: #293241;
        --color-text-muted: #4A5568;
        --color-primary: #A8E6CF;
        --color-primary-hover: #8FD9BE;
        --color-on-primary: #1B3B2B;
        --color-secondary: #CDB4DB;
        --color-surface-mint: #D8F3DC;
        --color-surface-lavender: #EDE4F5;
        --color-accent: #FFC8DD;
        --color-surface-pink: #FFF0F5;
        --color-eyebrow: #5B3E85;
        --color-logo-box: transparent;
        --hero-gradient: linear-gradient(112deg, #D8F3DC 0%, #EDE4F5 55%, #FFF0F5 100%);
        --hero-mascote-bg: rgba(255, 255, 255, 0.88);
        --flashcard-gradient: linear-gradient(135deg, #F4FBF7 0%, #F9F6FC 100%);
        --tldr-gradient: linear-gradient(135deg, #FFF9EB 0%, #FFF3F8 100%);
        --shadow-card: 0 4px 16px rgba(41, 50, 65, 0.05);
        color-scheme: light;
    """

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Fallback métrico da Inter (Arial ajustada): com display=swap o texto aparece
       imediatamente e a troca de fonte não altera altura/largura das linhas (CLS ~0). */
    @font-face {{
        font-family: 'Inter Fallback';
        src: local('Arial'), local('Helvetica'), local('Liberation Sans');
        ascent-override: 90.2%;
        descent-override: 22.48%;
        line-gap-override: 0%;
        size-adjust: 107.4%;
    }}

    :root {{
        {variaveis_tema_css}
        --radius-card: 16px;
        --radius-control: 10px;
    }}

    html, body, [class*="css"] {{
        font-family: 'Inter', 'Inter Fallback', system-ui, -apple-system, sans-serif;
        color: var(--color-text);
        background-color: var(--color-bg);
    }}

    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: var(--color-bg) !important;
        color: var(--color-text) !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: var(--color-surface) !important;
        border-right: 1px solid var(--color-border) !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: var(--color-text);
    }}

    /* Containers nativos com borda (Substituição estrutural dos Cards Fantasmas) */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: var(--color-surface) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-card) !important;
        padding: 24px !important;
        box-shadow: var(--shadow-card) !important;
        margin-bottom: 16px;
        transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }}

    /* Contraste WCAG AA (>= 4.5:1) para legendas, captions e textos secundários */
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p,
    .nm-sidebar-section-label,
    small {{
        color: var(--color-text-muted) !important;
        font-weight: 600 !important;
    }}

    .nm-sidebar-section-label {{
        font-size: 12px;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin: 12px 0 6px 0;
        display: block;
    }}

    /* Legenda da sidebar com contraste WCAG AA garantido (Lighthouse color-contrast) */
    .nm-sidebar-caption {{
        color: var(--color-text-muted) !important;
        font-size: 13px;
        font-weight: 600;
        line-height: 1.5;
        margin: 8px 0 0 0;
    }}
    .nm-sidebar-caption code {{
        color: var(--color-text) !important;
    }}

    /* Inputs, Selectbox, NumberInput, TextArea, FileUploader, Expander e Tabs para Light/Dark */
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div,
    [data-baseweb="base-input"],
    [data-baseweb="textarea"] {{
        background-color: var(--color-surface-alt) !important;
        color: var(--color-text) !important;
        border-color: var(--color-border) !important;
        border-radius: var(--radius-control) !important;
    }}
    [data-baseweb="select"] span,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {{
        color: var(--color-text) !important;
        -webkit-text-fill-color: var(--color-text) !important;
    }}
    [data-testid="stFileUploaderDropzone"] {{
        background-color: var(--color-surface-alt) !important;
        border: 1px dashed var(--color-border) !important;
        border-radius: var(--radius-card) !important;
        color: var(--color-text) !important;
    }}
    [data-testid="stExpander"] details {{
        background-color: var(--color-surface) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-control) !important;
    }}
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMetricValue"],
    [data-testid="stMetricLabel"] p {{
        color: var(--color-text) !important;
    }}

    /* Botões Primários e Secundários (WCAG AA + sem truncamento em mobile) */
    div.stButton > button,
    div.stFormSubmitButton > button,
    div.stDownloadButton > button {{
        white-space: normal !important;
        word-break: normal !important;
        height: auto !important;
        min-height: 44px !important;
        line-height: 1.35 !important;
        border-radius: var(--radius-control) !important;
        padding: 0.55rem 1rem !important;
        transition: all 0.2s ease;
    }}

    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {{
        background-color: var(--color-primary) !important;
        color: var(--color-on-primary) !important;
        border: 1px solid var(--color-primary-hover) !important;
        font-weight: 700 !important;
    }}
    div.stButton > button[kind="primary"] *,
    div.stFormSubmitButton > button[kind="primary"] * {{
        color: var(--color-on-primary) !important;
    }}
    div.stButton > button[kind="primary"]:hover,
    div.stFormSubmitButton > button[kind="primary"]:hover {{
        background-color: var(--color-primary-hover) !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.14);
    }}

    div.stButton > button[kind="secondary"],
    div.stDownloadButton > button {{
        background-color: var(--color-surface-lavender) !important;
        color: var(--color-text) !important;
        border: 1px solid var(--color-secondary) !important;
        font-weight: 600 !important;
    }}
    div.stButton > button[kind="secondary"] *,
    div.stDownloadButton > button * {{
        color: var(--color-text) !important;
    }}
    div.stButton > button[kind="secondary"]:hover,
    div.stDownloadButton > button:hover {{
        filter: brightness(0.97);
        box-shadow: 0 3px 8px rgba(15, 23, 42, 0.10);
    }}

    /* Componentes do Brandbook */
    .nm-brand-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 12px;
        min-height: {logo_h + 26}px; /* reserva a altura da logo antes do decode (CLS) */
        box-sizing: border-box;
        background: var(--color-logo-box);
        border-radius: var(--radius-card);
        border-bottom: 1px solid var(--color-border);
        margin-bottom: 12px;
    }}
    .nm-brand-container img {{
        max-width: 100%;
        height: auto;
        display: block;
    }}
    .nm-eyebrow {{
        font-size: 11.5px;
        color: var(--color-eyebrow);
        font-weight: 800;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }}
    .nm-section-title {{
        font-size: 1.28rem !important;
        font-weight: 800 !important;
        color: var(--color-text) !important;
        margin: 0 0 12px 0 !important;
        line-height: 1.3 !important;
    }}
    .nm-hero {{
        background: var(--hero-gradient);
        border-radius: 24px;
        padding: 30px 34px;
        border: 1px solid var(--color-border);
        margin-bottom: 24px;
        min-height: 200px; /* >= altura do mascote (136px) + padding: reserva o espaço do Hero (CLS) */
        box-sizing: border-box;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
        box-shadow: var(--shadow-card);
    }}
    .nm-hero-content {{
        flex: 1 1 320px;
        min-width: 0;
    }}
    .nm-hero h1 {{
        font-size: 1.85rem;
        font-weight: 800;
        color: var(--color-text) !important;
        margin: 6px 0 10px 0;
        letter-spacing: -0.6px;
        line-height: 1.25;
        word-break: normal;
        overflow-wrap: break-word;
        hyphens: none;
    }}
    .nm-hero p {{
        color: var(--color-text) !important;
        font-size: 0.96rem;
        margin: 0;
        max-width: 640px;
        line-height: 1.6;
        word-break: normal;
        overflow-wrap: break-word;
        hyphens: none;
    }}
    .nm-hero-mascote {{
        flex-shrink: 0;
        width: 136px;
        height: 136px;
        min-height: 136px;
        box-sizing: border-box;
        background: var(--hero-mascote-bg);
        border-radius: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
        padding: 10px;
    }}
    .nm-hero-mascote img {{
        max-width: 100%;
        max-height: 100%;
        width: auto;
        height: auto;
        object-fit: contain;
        display: block;
    }}
    .nm-card {{
        background: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-card);
        padding: 22px;
        box-shadow: var(--shadow-card);
        margin-bottom: 16px;
    }}
    .nm-stat-card {{
        background: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-card);
        padding: 18px 20px;
        min-height: 132px;
        box-sizing: border-box;
        contain: layout; /* isola reflow interno do card do restante da página */
        box-shadow: var(--shadow-card);
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    .nm-stat-icon {{
        font-size: 1.5rem;
        line-height: 1.2;
        margin-bottom: 4px;
    }}
    .nm-stat-value {{
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--color-text);
        margin: 4px 0 2px 0;
    }}
    .nm-stat-label {{
        font-size: 0.82rem;
        font-weight: 600;
        color: var(--color-text-muted);
    }}
    .nm-pill {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        color: var(--color-text);
        margin-right: 6px;
        margin-bottom: 6px;
        border: 1px solid var(--color-border);
    }}
    .nm-pill-mint {{ background-color: var(--color-surface-mint); }}
    .nm-pill-lavender {{ background-color: var(--color-surface-lavender); }}
    .nm-pill-pink {{ background-color: var(--color-surface-pink); }}
    .nm-badge-source {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        background: var(--color-surface-alt);
        border: 1px solid var(--color-border);
        border-radius: 6px;
        font-size: 11.5px;
        color: var(--color-text-muted);
        font-weight: 600;
        margin-top: 6px;
        margin-right: 6px;
    }}
    .nm-flashcard {{
        padding: 20px;
        background: var(--flashcard-gradient);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-card);
        margin-bottom: 10px;
        box-shadow: var(--shadow-card);
    }}
    .nm-step-card {{
        padding: 18px 20px;
        background: var(--color-surface);
        border-left: 4px solid var(--color-primary);
        border-top: 1px solid var(--color-border);
        border-right: 1px solid var(--color-border);
        border-bottom: 1px solid var(--color-border);
        border-radius: 0 var(--radius-card) var(--radius-card) 0;
        margin-bottom: 10px;
    }}
    .nm-tldr-box {{
        background: var(--tldr-gradient);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-card);
        padding: 20px;
        margin-bottom: 16px;
    }}
    .nm-sidebar-foot {{
        padding: 16px;
        background: var(--color-surface-mint);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-card);
        color: var(--color-text);
        font-size: 12.5px;
        line-height: 1.5;
        margin-top: 16px;
    }}
    .nm-note {{
        padding: 12px 16px;
        background: var(--color-surface-alt);
        border: 1px solid var(--color-border);
        border-radius: 12px;
        color: var(--color-text-muted);
        font-size: 12.5px;
        margin: 12px 0;
    }}

    /* Responsividade Mobile-First (Telas <= 768px / 360px) */
    @media (max-width: 768px) {{
        [data-testid="stMainBlockContainer"],
        .block-container {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1.5rem !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"] {{
            padding: 16px !important;
        }}
        .nm-hero {{
            flex-direction: column-reverse;
            text-align: center;
            padding: 22px 18px;
            gap: 14px;
            min-height: 340px; /* mascote + título em 2-3 linhas + parágrafo no mobile */
        }}
        .nm-hero-content {{
            flex: 1 1 100%;
            width: 100%;
        }}
        .nm-hero h1 {{
            font-size: 1.55rem;
            line-height: 1.25;
            max-width: 100%;
        }}
        .nm-hero p {{
            font-size: 0.92rem;
            max-width: 100%;
        }}
        .nm-hero-mascote {{
            width: 96px;
            height: 96px;
            min-height: 96px;
            margin: 0 auto;
        }}
        .nm-stat-card {{
            min-height: 112px;
            padding: 14px 16px;
            margin-bottom: 8px;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# 4. FUNÇÕES AUXILIARES DE DOCUMENTO E NORMALIZAÇÃO
# ==============================================================================
def navegar_para(pagina: str, limpar_ativo: bool = False) -> None:
    st.session_state["pagina_atual"] = pagina
    if limpar_ativo:
        st.session_state["resultado_ativo"] = None


def formatar_tamanho(num_bytes: int) -> str:
    if num_bytes < 1024:
        return f"{num_bytes} B"
    if num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes / (1024 * 1024):.2f} MB"


def extrair_previa_texto(doc: dict[str, Any], limite: int = 800) -> str:
    """Extrai trecho textual sob demanda para pré-visualização na Biblioteca."""
    if doc.get("previa_texto") is not None:
        return doc["previa_texto"]

    dados: bytes = doc.get("bytes", b"")
    ext: str = doc.get("ext", "")
    texto = ""
    try:
        if ext == "PDF":
            import pypdf  # import tardio: só carrega o parser quando a prévia é aberta

            reader = pypdf.PdfReader(io.BytesIO(dados))
            partes = []
            for pag in reader.pages[:3]:
                t = (pag.extract_text() or "").strip()
                if t:
                    partes.append(t)
            texto = "\n\n".join(partes) or "PDF sem camada de texto selecionável na prévia."
        else:
            try:
                texto = dados.decode("utf-8")
            except UnicodeDecodeError:
                texto = dados.decode("latin-1", errors="replace")
    except Exception as exc:
        texto = f"Não foi possível gerar prévia: {exc}"

    previa = texto[:limite] + ("..." if len(texto) > limite else "")
    doc["previa_texto"] = previa
    return previa


def registrar_documento(nome_arquivo: str, dados: bytes) -> tuple[bool, str]:
    """Valida extensão e limite de 20 MiB antes de adicionar documento à Biblioteca."""
    ext = Path(nome_arquivo).suffix.lower().lstrip(".")
    if ext not in config.EXTENSOES_SUPORTADAS:
        return False, f"Extensão não suportada em `{nome_arquivo}`. Envie PDF, TXT ou MD."
    if not dados:
        return False, f"O arquivo `{nome_arquivo}` está vazio."
    if len(dados) > config.MAX_UPLOAD_BYTES:
        return False, f"O arquivo `{nome_arquivo}` excede o limite de 20 MiB."

    doc_obj = {
        "id": f"doc-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "nome": nome_arquivo,
        "ext": ext.upper(),
        "bytes": dados,
        "tamanho": len(dados),
        "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "previa_texto": None,
    }
    st.session_state["documentos"].insert(0, doc_obj)
    oci_bridge.persistir_documento_original(nome_arquivo, dados)
    return True, f"`{nome_arquivo}` adicionado ({formatar_tamanho(len(dados))})."


def normalizar_resposta_api(
    resp: dict[str, Any],
    doc: dict[str, Any],
    qtd_itens: int,
) -> dict[str, Any]:
    """Converte resposta de `POST /geracoes` no modelo interno único do frontend."""
    return {
        "id": resp["geracao_id"],
        "formato": resp.get("formato", ""),
        "perfil": resp.get("perfil", ""),
        "nivel": resp.get("nivel_solicitado", ""),
        "documento_nome": doc["nome"],
        "quantidade_itens": qtd_itens,
        "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "duracao_ms": resp.get("duracao_ms"),
        "avaliacao_id": resp.get("avaliacao_id"),
        "adequacao": resp.get("adequacao") or {"divergencia": False, "mensagem": None},
        "conteudo": resp.get("conteudo"),
        "questoes": resp.get("questoes"),
        "armazenamento_oci": None,
    }


def _iniciar_disparo_geracao() -> None:
    """Callback para desabilitar o botão imediatamente antes do rerun de geração."""
    st.session_state["gerando"] = True
    st.session_state["_disparar_geracao"] = True


def _formatar_data_iso(iso_str: str | None) -> str:
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.astimezone().strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return iso_str


# ==============================================================================
# 5. SIDEBAR
# ==============================================================================
api_url = config.obter_api_base_url()

with st.sidebar:
    # A logo é o primeiro delta da sidebar: a sidebar é montada antes do health check
    # (I/O de rede), reduzindo o deslocamento horizontal do conteúdo principal (CLS).
    if tema_ativo == "dark" and logo_dark_b64:
        sb_logo_b64, sb_logo_w, sb_logo_h = logo_dark_b64, logo_dark_w, logo_dark_h
    else:
        sb_logo_b64, sb_logo_w, sb_logo_h = logo_b64, logo_w, logo_h

    if sb_logo_b64:
        st.markdown(
            f"<div class='nm-brand-container'>"
            f"<img src='{sb_logo_b64}' alt='Logo MentorIA-Tech' width='{sb_logo_w}' height='{sb_logo_h}' "
            f"decoding='async' "
            f"style='aspect-ratio: {sb_logo_w} / {sb_logo_h};'>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div class='nm-brand-container'>"
            "<span style='color: var(--color-text); font-size: 1.35rem; font-weight: 800;'>MentorIA-Tech</span>"
            "</div>",
            unsafe_allow_html=True,
        )

    rotulo_tema = "🌙 Modo Escuro" if tema_ativo == "light" else "☀️ Modo Claro"
    st.button(
        rotulo_tema,
        on_click=alternar_tema,
        use_container_width=True,
        type="secondary",
        key="btn_alternar_tema",
    )

    api_online = verificar_api_online(api_url)
    if api_online:
        st.success(f"🟢 API Online · `{api_url}`")
    else:
        st.error(f"🔴 API Offline · `{api_url}`")
        if st.button("↻ Testar conexão", use_container_width=True, key="btn_retestar_api"):
            verificar_api_online.clear()
            st.rerun()

    st.markdown("<span class='nm-sidebar-section-label'>NAVEGAÇÃO</span>", unsafe_allow_html=True)
    botoes_menu = {
        "Visão geral": "◫ Visão geral",
        "Minha biblioteca": "▤ Minha biblioteca",
        "Estúdio de criação": "✧ Estúdio de criação",
        "Meus conteúdos": "▣ Meus conteúdos",
    }
    for nome_rota, rotulo in botoes_menu.items():
        ativo = st.session_state["pagina_atual"] == nome_rota
        if st.button(rotulo, use_container_width=True, type="primary" if ativo else "secondary", key=f"nav_{nome_rota}"):
            navegar_para(nome_rota, limpar_ativo=(nome_rota != "Estúdio de criação"))
            st.rerun()

    identidade.renderizar_painel_identidade()

    st.markdown(
        "<div class='nm-sidebar-foot'>"
        "<strong>🌱 Aprender com clareza</strong>"
        "<p style='margin-top:6px; font-size: 12px; margin-bottom: 0;'>"
        "Transforme documentação técnica em experiências de aprendizagem com RAG e persistência na OCI."
        "</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    oci_status_txt = "OCI SDK/PAR pronto" if oci_bridge.OCI_DISPONIVEL else "Fallback local ativo"
    st.markdown(
        f"<p class='nm-sidebar-caption'>☁️ Bucket <code>{html.escape(config.obter_bucket_artefatos())}</code> · {oci_status_txt}</p>",
        unsafe_allow_html=True,
    )


st.markdown(
    f"<div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom: 12px; min-height: 32px;'>"
    f"<span style='color:var(--color-text-muted); font-size:14px; font-weight:600;'>MentorIA-Tech / <strong style='color:var(--color-text);'>{st.session_state['pagina_atual']}</strong></span>"
    f"<span class='nm-pill nm-pill-lavender'>✦ Hackathon ONE & Alura</span>"
    f"</div>",
    unsafe_allow_html=True,
)


# ==============================================================================
# 6. TELAS
# ==============================================================================
pagina = st.session_state["pagina_atual"]

# ------------------------------------------------------------------------------
# TELA 1: VISÃO GERAL
# ------------------------------------------------------------------------------
if pagina == "Visão geral":
    mascote_html = (
        f"<img src='{mascote_b64}' alt='Mascote MentorIA-Tech' width='{masc_w}' height='{masc_h}' "
        f"decoding='async' style='aspect-ratio: {masc_w} / {masc_h};'>"
        if mascote_b64
        else "<span role='img' aria-label='Mascote MentorIA-Tech'>🎓✨</span>"
    )
    st.markdown(
        f"<div class='nm-hero'>"
        f"<div class='nm-hero-content'>"
        f"<div class='nm-eyebrow'>BEM-VINDO AO MENTORIA-TECH ✦</div>"
        f"<h1>Aprender com clareza, leveza e autonomia.</h1>"
        f"<p>Transforme documentações técnicas densas em tutoriais, flashcards e quizzes interativos via pipeline RAG + LLM, com histórico no servidor e persistência na Oracle Cloud (OCI).</p>"
        f"</div>"
        f"<div class='nm-hero-mascote'>{mascote_html}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    col_a1, col_a2, col_a3, _ = st.columns([1.45, 1.55, 1.35, 0.65])
    if col_a1.button("1. 📂 Gerenciar Biblioteca →", type="primary", use_container_width=True, key="cta_biblioteca"):
        navegar_para("Minha biblioteca")
        st.rerun()
    if col_a2.button("2. ✦ Criar no Estúdio →", type="secondary", use_container_width=True, key="cta_estudio"):
        navegar_para("Estúdio de criação")
        st.rerun()
    if col_a3.button("3. 🗂️ Meus Conteúdos", type="secondary", use_container_width=True, key="cta_conteudos"):
        navegar_para("Meus conteúdos")
        st.rerun()
    st.write("")

    if api_online and st.session_state["quizzes_servidor"] is None:
        try:
            st.session_state["quizzes_servidor"] = api_client.listar_quizzes(
                usuario_id, base_url=api_url, session=obter_http_session()
            )
        except ApiError:
            st.session_state["quizzes_servidor"] = []

    qtd_quizzes_srv = len(st.session_state["quizzes_servidor"]) if st.session_state["quizzes_servidor"] is not None else "—"
    status_api_val = "Online" if api_online else "Offline"

    s1, s2, s3, s4 = st.columns(4)
    s1.markdown(
        f"<div class='nm-stat-card'><div class='nm-stat-icon' aria-hidden='true'>📂</div>"
        f"<div class='nm-stat-value'>{len(st.session_state['documentos'])}</div>"
        f"<div class='nm-stat-label'>Documentos na sessão</div></div>",
        unsafe_allow_html=True,
    )
    s2.markdown(
        f"<div class='nm-stat-card'><div class='nm-stat-icon' aria-hidden='true'>✨</div>"
        f"<div class='nm-stat-value'>{len(st.session_state['resultados'])}</div>"
        f"<div class='nm-stat-label'>Gerações nesta sessão</div></div>",
        unsafe_allow_html=True,
    )
    s3.markdown(
        f"<div class='nm-stat-card'><div class='nm-stat-icon' aria-hidden='true'>🎯</div>"
        f"<div class='nm-stat-value'>{qtd_quizzes_srv}</div>"
        f"<div class='nm-stat-label'>Quizzes salvos no servidor</div></div>",
        unsafe_allow_html=True,
    )
    s4.markdown(
        f"<div class='nm-stat-card'><div class='nm-stat-icon' aria-hidden='true'>☁️</div>"
        f"<div class='nm-stat-value'>{status_api_val}</div>"
        f"<div class='nm-stat-label'>API FastAPI · OCI {config.obter_bucket_artefatos()}</div></div>",
        unsafe_allow_html=True,
    )
    st.write("")

    c_rec, c_steps = st.columns([1.25, 1], gap="medium")
    with c_rec:
        with st.container(border=True):
            st.markdown("<h2 class='nm-section-title'>🌷 Gerações Recentes desta Sessão</h2>", unsafe_allow_html=True)
            if not st.session_state["resultados"]:
                st.info(
                    "🌱 Nenhum conteúdo gerado nesta sessão ainda. "
                    "Comece enviando um documento em **Minha biblioteca** e gere seu material no **Estúdio de criação**."
                )
            for r in st.session_state["resultados"][:4]:
                rc1, rc2 = st.columns([3.2, 1])
                rc1.markdown(
                    f"**{r['documento_nome']}** (`{r['formato']}`)\n\n"
                    f"<small>{r['perfil']} · {r['nivel']} · {r['criado_em']}</small>",
                    unsafe_allow_html=True,
                )
                if rc2.button("Abrir", key=f"dash_{r['id']}", use_container_width=True):
                    st.session_state["resultado_ativo"] = r
                    navegar_para("Estúdio de criação")
                    st.rerun()
                st.divider()

    with c_steps:
        with st.container(border=True):
            st.markdown("<h2 class='nm-section-title'>🚀 Próximas Evoluções (Roadmap)</h2>", unsafe_allow_html=True)
            st.markdown(
                "- 🌎 **App Trilíngue (PT-BR / ES / EN):** acessibilidade completa para toda a comunidade LATAM.\n"
                "- 🧩 **Extensão do Chrome & Bot Telegram:** estudar direto na aba da documentação e salvar na nuvem.\n"
                "- 📄 **Exportação `.pdf` / `.txt` & Power BI ativo:** reuso no NotebookLM e painel com avaliações em tempo real.\n"
                "- 🤖 **Agentes Conversacionais (`agents/`):** tutoria interativa multi-turno pós-MVP."
            )

    st.write("")
    c_onb, c_eq = st.columns([1.25, 1], gap="medium")
    with c_onb:
        with st.container(border=True):
            st.markdown("<h2 class='nm-section-title'>📘 Jornada de Criação & Guia Passo a Passo</h2>", unsafe_allow_html=True)
            st.markdown(
                "1. **Fontes (`Minha biblioteca`):** cole uma transcrição/texto (`+ Salvar Texto como .txt`), use `📘 Carregar exemplo real (Machine_Learning.pdf)` "
                "ou envie arquivos `.pdf`, `.md` ou `.txt` (até 20 MiB) em `📥 Adicionar à Biblioteca`.\n"
                "2. **Personalização & Geração (`Estúdio de criação`):** escolha o material, o perfil (`Iniciante`, `Jr/Pleno`, `Tech Lead`, `Gestor`), "
                "o nível e o formato pedagógico, e clique em `✦ Gerar Conteúdo Educacional com IA`.\n"
                "3. **Prática & Downloads:** confira as citações (`chunk_ids` e páginas), responda ao **Quiz Interativo** (3 tentativas sem gabarito antecipado) "
                "e baixe em **Markdown (`.md`)**, **CSV (Anki)** ou **JSON**.\n"
                "4. **Nuvem & Histórico (`Meus conteúdos`):** consulte o histórico no SQLite, inspecione o JSON e acompanhe o envio ao bucket **OCI (`mentoria-tech-artifacts`)**."
            )
            with st.expander("📖 Ver tutorial interativo completo (Trupeer · Andrea Gonzalez)"):
                st.markdown(
                    "- **Guia interativo passo a passo:** [Abrir no Trupeer](https://app.trupeer.ai/view/uApUfd7nr/criacao-de-conteudo-educacional-com-ia)\n"
                    "- **Documentação técnica:** `docs/tutorial-uso-mvp.md` no repositório."
                )

    with c_eq:
        with st.container(border=True):
            st.markdown("<h2 class='nm-section-title'>👥 Equipe 26 & Parcerias</h2>", unsafe_allow_html=True)
            st.markdown(
                "Interessado em parcerias, oportunidades ou evoluções do **MentorIA Tech**? "
                "Fale conosco pelo [GitHub Oficial](https://github.com/No-Country-simulation/G10-BRASIL-equipo-26)."
            )
            with st.expander("🤝 Conheça os 10 integrantes da Equipe 26", expanded=False):
                st.markdown(
                    "- **Lídia Moura** *(BI Analyst · Tech Lead)* — Liderança técnica, OCI, QA, BI & Documentação\n"
                    "- **Andrea De Nardi Gonzalez** *(Data Analyst)* — Compliance, Scrum Master & Tutorial MVP\n"
                    "- **Rodrigo Silva do Carmo** *(Data Scientist)* — Arquitetura RAG/LLM, Pydantic v2 & Benchmark\n"
                    "- **Wagner Julio de Campos** *(Full Stack)* — Front-end Streamlit, Integração & Lighthouse\n"
                    "- **Lysara Jacó Pinheiro** *(Data Analyst)* — Identidade de Marca, Brandbook UX/UI & Marketing\n"
                    "- **Marcos Vinicius Ferreira** *(Backend)* — Pipeline de ingestão e extração multi-formato\n"
                    "- **Vagner Marques** *(Data Analyst)* — Dados, schemas & exportação analítica BI\n"
                    "- **Leonardo Santos** *(Data Analyst)* — Suporte a dados e extração de documentos\n"
                    "- **Josiane da Silva** *(Full Stack)* & **João Okuyama** *(Data Analyst)* — Apoio inicial e repositório"
                )

    st.write("")
    with st.container(border=True):
        st.markdown("<h2 class='nm-section-title'>🎬 Vídeo Pitch & Demonstração (Modo Teatro)</h2>", unsafe_allow_html=True)
        video_pitch_url = config.obter_config(
            "MENTORIA_PITCH_VIDEO_URL",
            "https://youtu.be/jZzWt8NILnk",
        )
        st.video(video_pitch_url)
        st.caption(
            "Demonstração completa do MentorIA Tech em ação: ingestão de documentos técnicos (.pdf, .md e .txt), "
            "adaptação por perfil e formato pedagógico, Quiz interativo anti-alucinação e persistência na Oracle Cloud (OCI)."
        )

    st.write("")
    alura_key = "alura_dark" if tema_ativo == "dark" else "alura_light"
    alura_b64, alura_w, alura_h = carregar_asset_otimizado_b64(alura_key, max_size=(240, 90), display_height=34, padding=6)
    nc_b64, nc_w, nc_h = carregar_asset_otimizado_b64("nocountry", max_size=(260, 90), display_height=34, padding=6)
    one_b64, one_w, one_h = carregar_asset_otimizado_b64("one_oracle", max_size=(300, 90), display_height=38, padding=6)
    logos_rodape = []
    for b64, w, h, alt in (
        (one_b64, one_w, one_h, "Oracle Next Education (ONE)"),
        (alura_b64, alura_w, alura_h, "Alura"),
        (nc_b64, nc_w, nc_h, "NoCountry"),
    ):
        if b64:
            logos_rodape.append(
                f"<img src='{b64}' alt='{alt}' width='{w}' height='{h}' decoding='async' "
                f"style='height:{h}px; width:auto; object-fit:contain;'>"
            )
    if logos_rodape:
        st.markdown(
            "<div style='text-align:center; padding: 14px 12px 6px; opacity: 0.9;'>"
            "<div style='font-size:12px; color:var(--color-text-muted); margin-bottom:10px; font-weight:600; letter-spacing:0.05em;'>"
            "REALIZAÇÃO & PARCEIROS · HACKATHON ONE G10"
            "</div>"
            f"<div style='display:flex; justify-content:center; align-items:center; gap:28px; flex-wrap:wrap;'>{''.join(logos_rodape)}</div>"
            "</div>",
            unsafe_allow_html=True,
        )


# ------------------------------------------------------------------------------
# TELA 2: MINHA BIBLIOTECA
# ------------------------------------------------------------------------------
elif pagina == "Minha biblioteca":
    st.markdown("<div class='nm-eyebrow'>BASE DE CONHECIMENTO TÉCNICO</div>", unsafe_allow_html=True)
    st.title("Minha biblioteca 📂")
    st.write(
        "Carregue documentos técnicos originais em PDF, Markdown ou Texto (até 20 MiB) "
        "para envio integral via `multipart/form-data` ao pipeline RAG da API."
    )

    c_add, c_list = st.columns([1.2, 1], gap="large")

    with c_add:
        with st.container(border=True):
            st.markdown("<h2 class='nm-section-title'>➕ Upload de Documentos</h2>", unsafe_allow_html=True)
            arquivos = st.file_uploader(
                "Selecione arquivos técnicos (.pdf, .md, .txt — máx. 20 MiB)",
                accept_multiple_files=True,
                type=list(config.EXTENSOES_SUPORTADAS),
            )
            if arquivos and st.button("📥 Adicionar à Biblioteca", type="primary", use_container_width=True):
                sucessos = 0
                for arq in arquivos:
                    ok, msg = registrar_documento(arq.name, arq.getvalue())
                    if ok:
                        sucessos += 1
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")
                if sucessos:
                    st.rerun()

            if config.SAMPLE_PDF_PATH.exists():
                st.divider()
                st.markdown("### Documento de exemplo real do repositório:")
                if st.button("📘 Carregar exemplo real (Machine_Learning.pdf)", type="secondary", use_container_width=True):
                    try:
                        dados_pdf = config.SAMPLE_PDF_PATH.read_bytes()
                        ok, msg = registrar_documento(config.SAMPLE_PDF_PATH.name, dados_pdf)
                        if ok:
                            st.success(f"✅ {msg}")
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
                    except OSError as exc:
                        st.error(f"❌ Erro ao ler PDF de exemplo: {exc}")

            st.divider()
            st.markdown("### Ou adicione texto técnico manualmente:")
            t_man = st.text_input("Título do documento", placeholder="Ex: Guia de Redes VCN na OCI")
            c_man = st.text_area("Texto técnico da documentação", height=130, placeholder="Cole aqui o conteúdo técnico...")
            if st.button("+ Salvar Texto como .txt", type="secondary", use_container_width=True):
                if not t_man.strip() or not c_man.strip():
                    st.warning("Informe título e conteúdo antes de salvar.")
                else:
                    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", t_man.strip()).strip("_") or "documento"
                    ok, msg = registrar_documento(f"{slug}.txt", c_man.strip().encode("utf-8"))
                    if ok:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

    with c_list:
        with st.container(border=True):
            st.markdown(
                f"<h2 class='nm-section-title'>📚 Documentos Carregados ({len(st.session_state['documentos'])})</h2>",
                unsafe_allow_html=True,
            )
            if not st.session_state["documentos"]:
                st.info("Nenhum documento carregado nesta sessão. Faça upload ao lado ou carregue o PDF de exemplo.")

            for idx, doc in enumerate(st.session_state["documentos"]):
                fc1, fc2 = st.columns([3.5, 1])
                fc1.markdown(
                    f"📄 **{doc['nome']}**\n\n"
                    f"<small>{doc['ext']} · {formatar_tamanho(doc['tamanho'])} · {doc['criado_em']}</small>",
                    unsafe_allow_html=True,
                )
                if fc2.button("Excluir", key=f"del_{doc['id']}", use_container_width=True):
                    st.session_state["documentos"].pop(idx)
                    st.rerun()
                # Lazy: a extração de texto (pypdf) só roda quando a prévia é expandida
                exp_previa = st.expander(
                    f"Prévia textual de '{doc['nome']}'",
                    expanded=False,
                    key=f"exp_previa_{doc['id']}",
                    on_change="rerun",
                )
                with exp_previa:
                    if exp_previa.open:
                        st.text(extrair_previa_texto(doc))
                st.divider()


# ------------------------------------------------------------------------------
# TELA 3: ESTÚDIO DE CRIAÇÃO
# ------------------------------------------------------------------------------
elif pagina == "Estúdio de criação":
    st.markdown("<div class='nm-eyebrow'>TRANSFORMAÇÃO DIDÁTICA INTELIGENTE</div>", unsafe_allow_html=True)
    st.title("Estúdio de criação ✨")

    cf, cp = st.columns([0.95, 1.05], gap="large")

    with cf:
        with st.container(border=True):
            st.markdown("<h2 class='nm-section-title'>01 · Personalização</h2>", unsafe_allow_html=True)
            docs_lista = st.session_state["documentos"]
            docs_por_id = {d["id"]: d for d in docs_lista}

            if docs_lista:
                doc_sel_id = st.selectbox(
                    "Material de Origem:",
                    options=[d["id"] for d in docs_lista],
                    format_func=lambda did: f"{docs_por_id[did]['nome']} ({formatar_tamanho(docs_por_id[did]['tamanho'])})",
                )
                doc_escolhido = docs_por_id[doc_sel_id]
            else:
                doc_escolhido = None
                st.warning("Nenhum documento na Biblioteca. Carregue um arquivo na tela **Minha biblioteca** primeiro.")

            p1, p2 = st.columns(2)
            perfil_label = p1.selectbox("Perfil do Destinatário:", list(config.PERFIS.keys()))
            perfil_valor = config.PERFIS[perfil_label]

            nivel_label = p2.selectbox("Nível de Profundidade:", list(config.NIVEIS.keys()))
            nivel_valor = config.NIVEIS[nivel_label]

            qtd_itens = int(
                st.number_input(
                    "Quantidade de itens / questões:",
                    min_value=config.QTD_ITENS_MIN,
                    max_value=config.QTD_ITENS_MAX,
                    value=config.QTD_ITENS_PADRAO,
                    step=1,
                )
            )

            st.markdown("<h2 class='nm-section-title' style='margin-top: 16px !important;'>02 · Formato pedagógico</h2>", unsafe_allow_html=True)
            formato_label = st.radio("Formato de Saída:", list(config.FORMATOS.keys()))
            formato_valor = config.FORMATOS[formato_label]

            st.markdown(
                f"<div class='nm-note'>🛡️ <strong>Contrato v0.3:</strong> Envio via <code>POST /geracoes</code> "
                f"(<code>multipart/form-data</code>) + persistência no bucket OCI <code>{config.obter_bucket_artefatos()}</code>.</div>",
                unsafe_allow_html=True,
            )

            st.button(
                "✦ Gerar Conteúdo Educacional com IA" if not st.session_state["gerando"] else "⏳ Gerando conteúdo...",
                type="primary",
                use_container_width=True,
                disabled=(st.session_state["gerando"] or doc_escolhido is None),
                on_click=_iniciar_disparo_geracao,
                key="btn_gerar_conteudo",
            )

            if st.session_state.pop("_disparar_geracao", False):
                if doc_escolhido is None:
                    st.session_state["gerando"] = False
                    st.error("❌ Selecione um documento válido antes de gerar.")
                else:
                    try:
                        with st.status("Processando documento na API FastAPI (RAG + LLM)...", expanded=True) as status:
                            st.write(f"📤 Enviando `{doc_escolhido['nome']}` para `POST /geracoes`...")
                            resp_api = api_client.gerar_conteudo(
                                arquivo_nome=doc_escolhido["nome"],
                                arquivo_bytes=doc_escolhido["bytes"],
                                perfil=perfil_valor,
                                nivel=nivel_valor,
                                formato=formato_valor,
                                quantidade_itens=qtd_itens,
                                usuario_id=usuario_id,
                                sessao_id=sessao_id,
                                base_url=api_url,
                                session=obter_http_session(),
                            )
                            novo_res = normalizar_resposta_api(resp_api, doc_escolhido, qtd_itens)

                            st.write("☁️ Persistindo artefato no OCI Object Storage...")
                            oci_bridge.persistir_artefato(novo_res)

                            if novo_res["formato"] == "Quiz":
                                st.write("🎯 Preparando Quiz sem gabarito antecipado...")
                                quiz_ui.carregar_quiz(
                                    geracao_id=novo_res["id"],
                                    usuario_id=usuario_id,
                                    questoes=novo_res.get("questoes") or [],
                                    session=obter_http_session(),
                                )

                            status.update(label="Conteúdo gerado com sucesso!", state="complete", expanded=False)

                        st.session_state["resultados"].insert(0, novo_res)
                        st.session_state["resultado_ativo"] = novo_res
                        st.session_state["quizzes_servidor"] = None
                        st.session_state["gerando"] = False
                        st.rerun()
                    except ApiError as err:
                        st.error(f"❌ {err.mensagem_amigavel}")
                        if err.detalhes_tecnicos:
                            with st.expander("Detalhes técnicos do erro", expanded=False):
                                st.code(err.detalhes_tecnicos, language=None)
                    finally:
                        st.session_state["gerando"] = False

    with cp:
        with st.container(border=True):
            st.markdown("<h2 class='nm-section-title'>03 · Prévia e Estudo Interativo</h2>", unsafe_allow_html=True)
            res_ativo = st.session_state.get("resultado_ativo")

            if res_ativo:
                renderizadores.renderizar_cabecalho_resultado(res_ativo)
                if res_ativo.get("formato") == "Quiz":
                    quiz_ui.renderizar_quiz(
                        geracao_id=res_ativo["id"],
                        usuario_id=usuario_id,
                        sessao_id=sessao_id,
                        questoes_iniciais=res_ativo.get("questoes"),
                        key_prefix="studio",
                    )
                else:
                    renderizadores.renderizar_conteudo_nao_quiz(res_ativo)

                st.divider()
                st.markdown("### 📦 Exportar Conteúdo Gerado:")
                renderizadores.exportar_arquivos(
                    res_ativo,
                    prefixo_key="studio",
                    estado_quiz=st.session_state["quiz"].get(res_ativo["id"]),
                )
                renderizadores.renderizar_bloco_feedback(res_ativo, prefixo_key="studio")
            else:
                mascote_empty = (
                    f"<img src='{mascote_b64}' alt='Mascote MentorIA-Tech' width='{masc_w}' height='{masc_h}' "
                    f"decoding='async' loading='lazy' "
                    f"style='max-width: 110px; height: auto; aspect-ratio: {masc_w} / {masc_h}; margin: 0 auto; display: block;'>"
                    if mascote_b64
                    else "<span role='img' aria-label='Mascote MentorIA-Tech'>🪄</span>"
                )
                st.markdown(
                    f"<div style='text-align:center; padding: 42px 20px; color:var(--color-text-muted);'>"
                    f"<div style='margin-bottom: 16px;'>{mascote_empty}</div>"
                    f"<h3 style='color: var(--color-text); font-size: 1.2rem;'>Seu conteúdo aparecerá aqui</h3>"
                    f"<p style='max-width: 360px; margin: 0 auto; font-size: 14px; color: var(--color-text-muted);'>"
                    f"Selecione um documento ao lado e clique em 'Gerar Conteúdo' para consultar a API real."
                    f"</p>"
                    f"</div>",
                    unsafe_allow_html=True,
                )


# ------------------------------------------------------------------------------
# TELA 4: MEUS CONTEÚDOS
# ------------------------------------------------------------------------------
elif pagina == "Meus conteúdos":
    st.markdown("<div class='nm-eyebrow'>ACERVO DE OBJETOS EDUCACIONAIS</div>", unsafe_allow_html=True)
    st.title("Meus conteúdos 🌷")
    st.write(
        "Consulte os materiais gerados nesta sessão (todos os formatos) e os Quizzes "
        "persistidos no servidor para o seu `usuario_id`."
    )

    # Abas com estado (`on_change="rerun"`): apenas a aba ativa executa e envia seus
    # elementos ao navegador; a aba inativa não gera DOM nem chamadas à API (TBT menor).
    aba_sessao, aba_servidor = st.tabs(
        ["✨ Gerados nesta sessão", "🎯 Quizzes salvos no servidor (GET /quiz)"],
        key="tabs_meus_conteudos",
        on_change="rerun",
    )

    with aba_sessao:
        if aba_sessao.open:
            if not st.session_state["resultados"]:
                st.info("🗂️ Nenhum conteúdo gerado nesta sessão ainda. Acesse o **Estúdio de criação**.")

            for item in st.session_state["resultados"]:
                titulo_exp = f"✨ {item['documento_nome']} · {item['formato']} ({item['perfil']} / {item['nivel']}) — {item['criado_em']}"
                # Expander recolhido e lazy: o conteúdo (Quiz, JSON, exportações) só é
                # renderizado quando o usuário o expande.
                exp_item = st.expander(
                    titulo_exp,
                    expanded=False,
                    key=f"exp_sessao_{item['id']}",
                    on_change="rerun",
                )
                with exp_item:
                    if not exp_item.open:
                        continue

                    t1, t2, t3 = st.tabs(
                        ["📖 Visualização / Quiz", "🧾 JSON Estruturado", "☁️ OCI & Exportações"],
                        key=f"tabs_item_{item['id']}",
                        on_change="rerun",
                    )

                    with t1:
                        if t1.open:
                            renderizadores.renderizar_cabecalho_resultado(item)
                            if item["formato"] == "Quiz":
                                quiz_ui.renderizar_quiz(
                                    geracao_id=item["id"],
                                    usuario_id=usuario_id,
                                    sessao_id=sessao_id,
                                    questoes_iniciais=item.get("questoes"),
                                    key_prefix=f"hist_{item['id']}",
                                )
                            else:
                                renderizadores.renderizar_conteudo_nao_quiz(item)

                    with t2:
                        if t2.open:
                            st.json(oci_bridge.montar_pacote_artefato(item), expanded=2)

                    with t3:
                        if t3.open:
                            oci_info = item.get("armazenamento_oci") or {}
                            _, desc_oci = oci_bridge.rotulo_status_oci(oci_info)
                            st.markdown(
                                f"### ☁️ Oracle Cloud Infrastructure (OCI Object Storage)\n"
                                f"- **Bucket configurado:** `{oci_info.get('bucket', config.obter_bucket_artefatos())}`\n"
                                f"- **Objeto:** `{oci_info.get('objeto_id', '—')}`\n"
                                f"- **Status:** {desc_oci}"
                            )
                            st.divider()
                            renderizadores.exportar_arquivos(
                                item,
                                prefixo_key=f"acervo_{item['id']}",
                                estado_quiz=st.session_state["quiz"].get(item["id"]),
                            )

    with aba_servidor:
        if aba_servidor.open:
            col_txt, col_ref = st.columns([3, 1])
            col_txt.caption(f"Consultando até 30 quizzes recentes para `usuario_id={usuario_id}`.")
            if col_ref.button("🔄 Atualizar lista", use_container_width=True, key="btn_atualizar_quizzes_srv"):
                st.session_state["quizzes_servidor"] = None

            if st.session_state["quizzes_servidor"] is None:
                try:
                    st.session_state["quizzes_servidor"] = api_client.listar_quizzes(
                        usuario_id, base_url=api_url, session=obter_http_session()
                    )
                except ApiError as err:
                    st.error(f"❌ Não foi possível listar quizzes do servidor: {err.mensagem_amigavel}")
                    st.session_state["quizzes_servidor"] = []

            quizzes_srv = st.session_state.get("quizzes_servidor") or []
            if not quizzes_srv:
                st.info(
                    "Nenhum Quiz encontrado no servidor para o seu `usuario_id`. "
                    "Gere um Quiz no Estúdio ou recupere seu ID na sidebar."
                )

            nomes_sessao = {r["id"]: r["documento_nome"] for r in st.session_state["resultados"]}

            for qz in quizzes_srv:
                gid = qz["geracao_id"]
                doc_nome = nomes_sessao.get(gid)
                rotulo_doc = f" — {doc_nome}" if doc_nome else ""
                cab = f"🎯 Quiz `{gid[:8]}`{rotulo_doc} · {qz.get('perfil')} / {qz.get('nivel')} · {_formatar_data_iso(qz.get('data_hora'))}"
                # Lazy: `GET /quiz/{id}` e o histórico só são consultados ao expandir o item.
                exp_srv = st.expander(cab, expanded=False, key=f"exp_srv_{gid}", on_change="rerun")
                with exp_srv:
                    if not exp_srv.open:
                        continue

                    c_open, _ = st.columns([1.4, 2.6])
                    if c_open.button("Abrir no Estúdio", key=f"open_srv_{gid}", type="secondary", use_container_width=True):
                        try:
                            dados_q = api_client.consultar_quiz(gid, usuario_id, base_url=api_url, session=obter_http_session())
                            st.session_state["resultado_ativo"] = {
                                "id": gid,
                                "formato": "Quiz",
                                "perfil": qz.get("perfil", ""),
                                "nivel": qz.get("nivel", ""),
                                "documento_nome": doc_nome or f"Quiz {gid[:8]}",
                                "quantidade_itens": len(dados_q.get("questoes") or []),
                                "criado_em": _formatar_data_iso(qz.get("data_hora")),
                                "duracao_ms": None,
                                "avaliacao_id": None,
                                "adequacao": {"divergencia": False, "mensagem": None},
                                "conteudo": None,
                                "questoes": dados_q.get("questoes") or [],
                                "armazenamento_oci": None,
                            }
                            navegar_para("Estúdio de criação")
                            st.rerun()
                        except ApiError as err:
                            st.error(f"❌ {err.mensagem_amigavel}")

                    quiz_ui.renderizar_quiz(
                        geracao_id=gid,
                        usuario_id=usuario_id,
                        sessao_id=sessao_id,
                        questoes_iniciais=None,
                        key_prefix=f"srv_{gid}",
                    )
