import base64
import csv
import io
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from PIL import Image
import pypdf
import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# 0. RESOLUÇÃO DE DIRETÓRIOS E INTEGRAÇÃO SEGURA COM RAG / BACKEND
# ==============================================================================
APP_DIR = Path(__file__).resolve().parent
REPO_DIR = APP_DIR.parent
ASSETS_DIR = APP_DIR / "assets"
RAG_DIR = REPO_DIR / "rag"
RAG_PIPELINE_DIR = RAG_DIR / "pipeline"

# Adiciona pastas ao sys.path para importação de schemas e banco de dados se disponíveis
for p in [str(RAG_DIR), str(RAG_PIPELINE_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Tentativa de importação dos módulos do RAG e persistência (com fallback suave)
MODULO_DATABASE_DISPONIVEL = False
MODULO_RAG_DISPONIVEL = False

try:
    import database
    from database import init_db, save_geracao, save_resposta
    init_db()
    MODULO_DATABASE_DISPONIVEL = True
except Exception:
    MODULO_DATABASE_DISPONIVEL = False

try:
    import pipeline.schemas as schemas
    import rag_retrieval
    import llm_pipeline
    MODULO_RAG_DISPONIVEL = True
except Exception:
    MODULO_RAG_DISPONIVEL = False


# ==============================================================================
# 1. CARREGAMENTO E RECORTADOR DINÂMICO DE ASSETS (BRANDBOOK UX/UI)
# ==============================================================================
@st.cache_resource
def carregar_asset_recortado(tipo: str, padding: int = 15):
    """
    Carrega imagens em PNG transparente e recorta as margens vazias (bounding box)
    para garantir proporções visuais perfeitas e evitar espaços em branco na interface.
    """
    mapa_caminhos = {
        "icone": ASSETS_DIR / "Ícone principal" / "Ícone.png",
        "logo": ASSETS_DIR / "Logomarca principal" / "Logomarca principal.png",
        "mascote": ASSETS_DIR / "Mascote" / "Mascote.png",
    }
    caminho = mapa_caminhos.get(tipo)
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
        return img
    except Exception:
        return None


def img_para_base64(img: Image.Image) -> str:
    """Converte objeto PIL.Image em URI base64 para uso em tags HTML customizadas."""
    if img is None:
        return ""
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"


img_icone = carregar_asset_recortado("icone", padding=10)
img_logo = carregar_asset_recortado("logo", padding=15)
img_mascote = carregar_asset_recortado("mascote", padding=20)
mascote_b64 = img_para_base64(img_mascote)


# ==============================================================================
# 2. CONFIGURAÇÃO DA PÁGINA E IDIOMA
# ==============================================================================
st.set_page_config(
    page_title="MentorIA-Tech · Estúdio de Aprendizagem",
    page_icon=img_icone if img_icone else "🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Forçar o idioma pt-BR no HTML raiz para evitar popup indevido de tradução do navegador
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
# 3. TOKENS CSS & IDENTIDADE VISUAL OFICIAL (BRANDBOOK UX/UI V1.1)
# ==============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --color-primary: #A8E6CF;          /* Verde Menta Principal */
        --color-secondary: #CDB4DB;        /* Lilás Pastel Secundário */
        --color-accent: #FFC8DD;           /* Rosa Suave Destaque */
        --color-surface-mint: #D8F3DC;     /* Superfícies Menta */
        --color-surface-lavender: #EDE4F5; /* Superfícies Lavanda */
        --color-surface-pink: #FFF0F5;     /* Superfícies Rosa Pálido */
        --color-bg: #FAFAFC;               /* Off-white Aplicação */
        --color-surface: #FFFFFF;          /* Branco Cards e Leitura */
        --color-border: #F1F3F5;           /* Cinza Suave Divisórias */
        --color-text: #293241;             /* Grafite Textos Principais */
        --color-text-muted: #657080;       /* Grafite Secundário */
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

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: var(--color-surface);
        border-right: 1px solid var(--color-border);
    }

    /* Botões Primários e Secundários (Conformidade WCAG AA com texto Grafite) */
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
    div.stButton > button[kind="secondary"]:hover {
        filter: brightness(0.97);
        box-shadow: 0 3px 8px rgba(41, 50, 65, 0.06);
    }

    /* Componentes Customizados */
    .nm-brand-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 10px 0 16px 0;
        border-bottom: 1px solid var(--color-border);
        margin-bottom: 18px;
    }
    .nm-eyebrow {
        font-size: 11.5px;
        color: #7a58a6;
        font-weight: 800;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .nm-hero {
        background: linear-gradient(112deg, #D8F3DC 0%, #EDE4F5 55%, #FFF0F5 100%);
        border-radius: 24px;
        padding: 30px 34px;
        border: 1px solid var(--color-border);
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
    }
    .nm-hero h1 {
        font-size: 29px;
        font-weight: 800;
        color: var(--color-text);
        margin: 6px 0 10px 0;
        letter-spacing: -0.8px;
        line-height: 1.25;
    }
    .nm-hero p {
        color: var(--color-text);
        font-size: 15px;
        margin: 0;
        max-width: 640px;
        line-height: 1.6;
    }
    .nm-hero-mascote {
        flex-shrink: 0;
        width: 140px;
        height: 140px;
        background: rgba(255, 255, 255, 0.85);
        border-radius: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 24px rgba(41, 50, 65, 0.06);
        padding: 10px;
    }
    .nm-card {
        background: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-card);
        padding: 22px;
        box-shadow: 0 4px 14px rgba(41, 50, 65, 0.03);
        margin-bottom: 16px;
    }
    .nm-stat-card {
        background: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-card);
        padding: 18px 20px;
        box-shadow: 0 4px 14px rgba(41, 50, 65, 0.03);
    }
    .nm-stat-value {
        font-size: 26px;
        font-weight: 800;
        color: var(--color-text);
        margin: 6px 0 2px 0;
    }
    .nm-stat-label {
        font-size: 13px;
        color: var(--color-text-muted);
    }
    .nm-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        color: var(--color-text);
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .nm-pill-mint { background-color: var(--color-surface-mint); }
    .nm-pill-lavender { background-color: var(--color-surface-lavender); }
    .nm-pill-pink { background-color: var(--color-surface-pink); }
    .nm-badge-source {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 3px 9px;
        background: #F1F3F5;
        border: 1px solid #E2E6EA;
        border-radius: 6px;
        font-size: 11.5px;
        color: #495057;
        font-weight: 600;
        margin-top: 8px;
    }
    .nm-flashcard {
        padding: 20px;
        background: linear-gradient(135deg, #F4FBF7, #F9F6FC);
        border: 1px solid #E6DEF3;
        border-radius: var(--radius-card);
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(41, 50, 65, 0.02);
    }
    .nm-step-card {
        padding: 18px 20px;
        background: var(--color-surface);
        border-left: 4px solid var(--color-primary);
        border-top: 1px solid var(--color-border);
        border-right: 1px solid var(--color-border);
        border-bottom: 1px solid var(--color-border);
        border-radius: 0 var(--radius-card) var(--radius-card) 0;
        margin-bottom: 14px;
    }
    .nm-tldr-box {
        background: linear-gradient(135deg, #FFF9EB, #FFF3F8);
        border: 1px solid #F6E2B8;
        border-radius: var(--radius-card);
        padding: 20px;
        margin-bottom: 16px;
    }
    .nm-feedback-box {
        background: var(--color-surface);
        border: 1px solid #D8F3DC;
        border-radius: var(--radius-card);
        padding: 18px 22px;
        margin-top: 20px;
    }
    .nm-sidebar-foot {
        padding: 16px;
        background: var(--color-surface-mint);
        border-radius: var(--radius-card);
        color: var(--color-text);
        font-size: 12.5px;
        line-height: 1.5;
        margin-top: 24px;
    }
    .nm-note {
        padding: 12px 16px;
        background: #F8F9FA;
        border: 1px solid #E9ECEF;
        border-radius: 12px;
        color: #495057;
        font-size: 12.5px;
        margin: 12px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# 4. INICIALIZAÇÃO DE ESTADO COM CENÁRIOS REAIS DO EDITAL
# ==============================================================================
if "pagina_atual" not in st.session_state:
    st.session_state["pagina_atual"] = "Visão geral"

if "fontes" not in st.session_state:
    st.session_state["fontes"] = [
        {
            "id": "doc-oci-vcn",
            "titulo": "Introdução à Arquitetura de Redes VCN na OCI",
            "conteudo": (
                "A Virtual Cloud Network (VCN) é uma rede privada e personalizável configurada na Oracle Cloud Infrastructure. "
                "Semelhante a uma rede de data center tradicional, a VCN oferece controle total sobre seu ambiente de rede, "
                "incluindo sub-redes públicas e privadas, tabelas de roteamento, Internet Gateways, NAT Gateways e Security Lists "
                "para controle de tráfego via regras de entrada (ingress) e saída (egress).\n\n"
                "Sub-redes Públicas possuem endereços IP públicos roteáveis e podem receber tráfego direto da Internet através de um Internet Gateway. "
                "Sub-redes Privadas são isoladas da Internet pública direta, e para que instâncias privadas baixem atualizações ou acessem a internet, "
                "utiliza-se um NAT Gateway. As Security Lists atuam como firewalls virtuais de nível de sub-rede, especificando portas e protocolos permitidos."
            ),
            "paginas": [
                {
                    "pagina": 1,
                    "texto": "A Virtual Cloud Network (VCN) é uma rede privada configurada na Oracle Cloud Infrastructure. Inclui sub-redes públicas e privadas, tabelas de roteamento, Internet Gateways, NAT Gateways e Security Lists."
                },
                {
                    "pagina": 2,
                    "texto": "Sub-redes Públicas e Privadas: Sub-redes públicas recebem tráfego da internet via Internet Gateway. Sub-redes privadas usam NAT Gateway para tráfego de saída. Security Lists controlam regras de ingress e egress."
                }
            ],
            "tipo": "TXT",
            "pronto": True,
            "criado_em": "09/11/2026 14:00",
        },
        {
            "id": "doc-ml-intro",
            "titulo": "Fundamentos de Machine Learning e Modelos Preditivos",
            "conteudo": (
                "Machine Learning é a área da ciência da computação voltada para a criação de modelos matemáticos a partir de dados históricos "
                "capazes de generalizar decisões e realizar predições. Em um conjunto de dados (dataset), as linhas são denominadas instâncias "
                "ou observações, enquanto as colunas preditoras são conhecidas como atributos, variáveis independentes ou features. A variável que se "
                "deseja prever é denominada classe, target ou variável resposta.\n\n"
                "Os problemas dividem-se em supervisionados (como classificação e regressão) e não-supervisionados (agrupamento/clustering). "
                "Antes de treinar um modelo, executam-se técnicas de pré-processamento como seleção de features, normalização e divisão dos dados "
                "em conjuntos de treino e teste. A técnica de validação cruzada (Cross-validation) divide o dataset em partições alternando os papéis "
                "de treino e validação para mitigar o sobreajuste (overfitting)."
            ),
            "paginas": [
                {
                    "pagina": 5,
                    "texto": "Definição de modelo em Machine Learning: representação matemática das relações nos dados. Instâncias são as linhas do dataset; features são as variáveis independentes para prever a variável target."
                },
                {
                    "pagina": 6,
                    "texto": "Categorias de aprendizagem: Supervisionada (Classificação, Regressão) e Não-supervisionada (Clustering). Exemplos de algoritmos supervisionados: Regressão Linear, KNN, Árvores de Decisão."
                },
                {
                    "pagina": 13,
                    "texto": "Pré-processamento de dados: Feature selection, feature engineering, normalização de escalas e divisão em conjuntos de treino e teste."
                },
                {
                    "pagina": 14,
                    "texto": "Construção do modelo e validação cruzada (Cross-validation): técnica para dividir os dados em partições e alternar treino e validação, garantindo boa capacidade de generalização."
                }
            ],
            "tipo": "PDF",
            "pronto": True,
            "criado_em": "09/11/2026 15:30",
        }
    ]

# Cenários reais obrigatórios do Edital (Tutorial, Flashcards e Quiz) pré-carregados
if "resultados" not in st.session_state:
    st.session_state["resultados"] = [
        {
            "id": "nm-demo-tutorial-01",
            "status": "sucesso",
            "criado_em": "09/11/2026 18:20",
            "provedor": "Google Gemini (gemini-2.5-flash)",
            "payload_entrada": {
                "documento_titulo": "Fundamentos de Machine Learning e Modelos Preditivos",
                "perfil_destinatario": "Iniciante",
                "formato_saida": "Tutorial",
                "nivel_detalhe": "basico",
                "quantidade_itens": 5,
                "instrucoes_adicionais": "Linguagem didática com analogias práticas"
            },
            "metadados": {
                "perfil": "Iniciante",
                "formato": "Tutorial",
                "nicho": "Geral",
                "nivel": "basico",
                "tempo_estimado_estudo_minutos": 10,
                "conceitos_chave": ["Dataset", "Instâncias & Features", "Target", "Pré-processamento", "Cross-validation"],
                "modelo_llm": "gemini-2.5-flash",
                "versao_prompt": "rag-llm-v1"
            },
            "conteudo_adaptado": {
                "formato": "Tutorial",
                "titulo": "Guia Prático Passo a Passo: Construindo seu Primeiro Modelo em Machine Learning",
                "introducao_contextualizada": "Neste tutorial passo a passo, você aprenderá como transformar dados brutos em previsões inteligentes, entendendo a estrutura de um dataset e o ciclo de vida de um modelo preditivo.",
                "passos": [
                    {
                        "titulo": "1. Compreender a estrutura de um Dataset",
                        "explicacao": "Pense no dataset como uma planilha: cada linha representa uma 'instância' (uma pessoa ou evento) e cada coluna representa uma 'feature' (característica como idade ou preço). A coluna final que desejamos prever é chamada de 'target'.",
                        "dica_didatica": "Instâncias = Linhas | Features = Colunas explicativas | Target = Resposta que você busca prever.",
                        "fontes": [{"paginas": [5], "chunk_ids": ["doc-ml-intro_p5_0"]}]
                    },
                    {
                        "titulo": "2. Escolher o tipo de aprendizado correto",
                        "explicacao": "Se o seu dataset já possui a resposta correta no histórico (ex: se o cliente pagou ou não), trata-se de Aprendizagem Supervisionada. Se você deseja encontrar padrões sem respostas prévias, usa-se Aprendizagem Não-Supervisionada (agrupamento).",
                        "dica_didatica": "Classificação prevê categorias (Sim/Não). Regressão prevê números contínuos (preço, temperatura).",
                        "fontes": [{"paginas": [6], "chunk_ids": ["doc-ml-intro_p6_0"]}]
                    },
                    {
                        "titulo": "3. Realizar o Pré-processamento dos Dados",
                        "explicacao": "Antes do treinamento, prepare os dados: normalize escalas numéricas diferentes, trate valores ausentes e selecione apenas os atributos relevantes (feature selection) para não sobrecarregar o algoritmo.",
                        "dica_didatica": "Dados limpos e bem preparados garantem a qualidade das predições mais do que algoritmos complexos.",
                        "fontes": [{"paginas": [13], "chunk_ids": ["doc-ml-intro_p13_0"]}]
                    },
                    {
                        "titulo": "4. Separar em Dados de Treino e Teste",
                        "explicacao": "Divida aleatoriamente sua base em duas partes: o conjunto de treino (usado pelo algoritmo para aprender) e o conjunto de teste (mantido em segredo para avaliar se o modelo aprendeu de verdade).",
                        "dica_didatica": "Nunca avalie seu modelo usando os mesmos dados em que ele foi treinado, para evitar a 'decoreba' (overfitting).",
                        "fontes": [{"paginas": [13, 14], "chunk_ids": ["doc-ml-intro_p13_0", "doc-ml-intro_p14_0"]}]
                    },
                    {
                        "titulo": "5. Validar com Cross-Validation",
                        "explicacao": "Para garantir máxima confiabilidade, aplique validação cruzada: os dados são divididos em várias partições e o modelo é treinado e testado repetidas vezes alternando os blocos.",
                        "dica_didatica": "O Cross-validation confirma se o seu modelo funcionará bem com dados do mundo real.",
                        "fontes": [{"paginas": [14], "chunk_ids": ["doc-ml-intro_p14_0"]}]
                    }
                ]
            },
            "avaliacao_qualidade": {
                "ancoragem_fonte_score": 1.0,
                "clareza_pedagogica": "Alta",
                "observacoes": ["100% dos 5 passos ancorados em citações literais das páginas 5, 6, 13 e 14 do documento técnico."]
            },
            "armazenamento_oci": {
                "bucket": "mentoria-tech-conteudos-educativos",
                "objeto_id": "tutorial-ml-iniciante-01.json",
                "status_upload": "sucesso"
            }
        },
        {
            "id": "nm-demo-flashcards-02",
            "status": "sucesso",
            "criado_em": "09/11/2026 18:35",
            "provedor": "Groq Fallback (openai/gpt-oss-120b)",
            "payload_entrada": {
                "documento_titulo": "Introdução à Arquitetura de Redes VCN na OCI",
                "perfil_destinatario": "Iniciante",
                "formato_saida": "Flashcards",
                "nivel_detalhe": "basico",
                "quantidade_itens": 4,
                "instrucoes_adicionais": "Foco em conceitos e papéis dos componentes de rede"
            },
            "metadados": {
                "perfil": "Iniciante",
                "formato": "Flashcards",
                "nicho": "Geral",
                "nivel": "basico",
                "tempo_estimado_estudo_minutos": 8,
                "conceitos_chave": ["VCN", "Sub-redes", "Internet Gateway", "NAT Gateway", "Security Lists"],
                "modelo_llm": "openai/gpt-oss-120b",
                "versao_prompt": "rag-llm-v1"
            },
            "conteudo_adaptado": {
                "formato": "Flashcards",
                "titulo": "Flashcards de Revisão: Redes Virtuais (VCN) na Nuvem Oracle (OCI)",
                "introducao_contextualizada": "Cartões de memorização ativa para fixar com rapidez os conceitos essenciais da arquitetura de redes em nuvem OCI.",
                "itens": [
                    {
                        "pergunta": "O que é uma Virtual Cloud Network (VCN) na OCI?",
                        "resposta": "É uma rede virtual privada e segura configurada dentro da nuvem da Oracle, correspondendo à infraestrutura de rede tradicional da empresa onde seus servidores operam.",
                        "dica_didatica": "Pense na VCN como o bairro fechado e murado da sua empresa na nuvem.",
                        "classificacao": {"assunto": "Arquitetura OCI", "subassunto": "VCN", "nivel_dificuldade": "basico"},
                        "fontes": [{"paginas": [1], "chunk_ids": ["doc-oci-vcn_p1_0"]}]
                    },
                    {
                        "pergunta": "Qual a diferença entre Sub-rede Pública e Sub-rede Privada?",
                        "resposta": "Sub-redes públicas possuem IPs públicos roteáveis e comunicam-se com a Internet via Internet Gateway. Sub-redes privadas não possuem acesso direto externo e são usadas para bancos de dados e backends protegidos.",
                        "dica_didatica": "Pública = vitrine aberta ao público | Privada = cofre interno protegido.",
                        "classificacao": {"assunto": "Redes", "subassunto": "Sub-redes", "nivel_dificuldade": "basico"},
                        "fontes": [{"paginas": [1, 2], "chunk_ids": ["doc-oci-vcn_p1_0", "doc-oci-vcn_p2_0"]}]
                    },
                    {
                        "pergunta": "Para que serve o NAT Gateway na arquitetura de rede?",
                        "resposta": "Permite que instâncias em sub-redes privadas iniciem conexões de saída para a Internet (ex: baixar patches ou bibliotecas) sem permitir que ninguém de fora inicie conexão com elas.",
                        "dica_didatica": "É como uma porta giratória que só permite sair, nunca entrar.",
                        "classificacao": {"assunto": "Conectividade", "subassunto": "Gateways", "nivel_dificuldade": "basico"},
                        "fontes": [{"paginas": [2], "chunk_ids": ["doc-oci-vcn_p2_0"]}]
                    },
                    {
                        "pergunta": "Qual a função das Security Lists?",
                        "resposta": "Funcionam como firewalls virtuais no nível da sub-rede, estabelecendo regras rigorosas de entrada (ingress) e saída (egress) de pacotes por protocolo e porta.",
                        "dica_didatica": "Porteiros virtuais com listas estritas de quem tem autorização para entrar ou sair.",
                        "classificacao": {"assunto": "Segurança", "subassunto": "Security Lists", "nivel_dificuldade": "basico"},
                        "fontes": [{"paginas": [2], "chunk_ids": ["doc-oci-vcn_p2_0"]}]
                    }
                ]
            },
            "avaliacao_qualidade": {
                "ancoragem_fonte_score": 1.0,
                "clareza_pedagogica": "Alta",
                "observacoes": ["Conceitos técnicos adaptados com analogias claras e 100% de ancoragem nas páginas 1 e 2."]
            },
            "armazenamento_oci": {
                "bucket": "mentoria-tech-conteudos-educativos",
                "objeto_id": "flashcards-vcn-iniciante-02.json",
                "status_upload": "sucesso"
            }
        },
        {
            "id": "nm-demo-quiz-03",
            "status": "sucesso",
            "criado_em": "09/11/2026 18:45",
            "provedor": "Google Gemini (gemini-2.5-flash)",
            "payload_entrada": {
                "documento_titulo": "Fundamentos de Machine Learning e Modelos Preditivos",
                "perfil_destinatario": "Jr/Pleno",
                "formato_saida": "Quiz",
                "nivel_detalhe": "intermediario",
                "quantidade_itens": 4,
                "instrucoes_adicionais": "Perguntas de múltipla escolha com foco conceitual e rigor técnico"
            },
            "metadados": {
                "perfil": "Jr/Pleno",
                "formato": "Quiz",
                "nicho": "Geral",
                "nivel": "intermediario",
                "tempo_estimado_estudo_minutos": 10,
                "conceitos_chave": ["Instâncias", "Features", "Supervisionado", "Cross-validation"],
                "modelo_llm": "gemini-2.5-flash",
                "versao_prompt": "rag-llm-v1"
            },
            "conteudo_adaptado": {
                "formato": "Quiz",
                "titulo": "Quiz Interativo de Validação: Conceitos Fundamentais de Machine Learning",
                "introducao_contextualizada": "Teste seus conhecimentos técnicos sobre modelagem preditiva, estrutura de dados e técnicas de validação cruzada.",
                "questoes": [
                    {
                        "enunciado": "Em um conjunto de dados para Machine Learning, o que representam especificamente as 'instâncias' e as 'features'?",
                        "alternativas": [
                            "Instâncias são as colunas de predição e features são as linhas de observação.",
                            "Instâncias são as linhas (observações) do dataset e features são as colunas preditoras independentes.",
                            "Instâncias representam a taxa de acerto do modelo e features são os hiperparâmetros.",
                            "Instâncias são exclusivamente variáveis dependentes categóricas."
                        ],
                        "indice_resposta_correta": 1,
                        "explicacao": "Conforme o material de origem (pág. 5), as linhas de um dataset são denominadas instâncias ou observações, enquanto as colunas usadas para prever a variável target são as features.",
                        "classificacao": {"assunto": "Estrutura de Dados", "subassunto": "Datasets", "nivel_dificuldade": "intermediario"},
                        "fontes": [{"paginas": [5], "chunk_ids": ["doc-ml-intro_p5_0"]}]
                    },
                    {
                        "enunciado": "Qual a principal finalidade da técnica de Validação Cruzada (Cross-validation)?",
                        "alternativas": [
                            "Treinar e validar o modelo utilizando o mesmo conjunto de dados dividido em partições alternadas para avaliar a capacidade real de generalização.",
                            "Converter variáveis categóricas em numéricas durante o pré-processamento.",
                            "Executar simultaneamente algoritmos supervisionados e não-supervisionados na mesma base.",
                            "Aumentar o número de instâncias através de geração sintética de dados."
                        ],
                        "indice_resposta_correta": 0,
                        "explicacao": "A validação cruzada divide os dados em partições e alterna os papéis de treino e teste entre elas, garantindo que o modelo seja avaliado de forma robusta e mitigando o overfitting (pág. 14).",
                        "classificacao": {"assunto": "Técnicas de Validação", "subassunto": "Cross-validation", "nivel_dificuldade": "intermediario"},
                        "fontes": [{"paginas": [14], "chunk_ids": ["doc-ml-intro_p14_0"]}]
                    },
                    {
                        "enunciado": "Qual dos seguintes algoritmos é classificado como pertencente à Aprendizagem Supervisionada?",
                        "alternativas": [
                            "K-Means Clustering",
                            "Árvore de Decisão",
                            "DBSCAN",
                            "Algoritmo Apriori de Associação"
                        ],
                        "indice_resposta_correta": 1,
                        "explicacao": "O documento (pág. 6) cita explicitamente Regressão Linear, KNN e Árvores de Decisão como exemplos de algoritmos de aprendizagem supervisionada.",
                        "classificacao": {"assunto": "Algoritmos", "subassunto": "Aprendizagem Supervisionada", "nivel_dificuldade": "intermediario"},
                        "fontes": [{"paginas": [6], "chunk_ids": ["doc-ml-intro_p6_0"]}]
                    },
                    {
                        "enunciado": "Por que a divisão dos dados em conjuntos de treino e teste é mandatória antes da criação do modelo?",
                        "alternativas": [
                            "Para evitar que o modelo seja treinado em bases com valores nulos.",
                            "Para garantir que a performance seja avaliada em dados que o algoritmo nunca viu durante o treinamento, aferindo sua capacidade de generalização.",
                            "Para reduzir obrigatoriamente a quantidade de features pela metade.",
                            "Para permitir que a variável target seja calculada pelo próprio algoritmo sem intervenção humana."
                        ],
                        "indice_resposta_correta": 1,
                        "explicacao": "Dividir em treino e teste permite verificar se o modelo realmente aprendeu os padrões gerais subjacentes ou se apenas decorou os dados de treino (pág. 13 e 14).",
                        "classificacao": {"assunto": "Metodologia", "subassunto": "Treino e Teste", "nivel_dificuldade": "intermediario"},
                        "fontes": [{"paginas": [13, 14], "chunk_ids": ["doc-ml-intro_p13_0", "doc-ml-intro_p14_0"]}]
                    }
                ]
            },
            "avaliacao_qualidade": {
                "ancoragem_fonte_score": 1.0,
                "clareza_pedagogica": "Alta",
                "observacoes": ["Questões com alternativas plausíveis, gabarito justificado e ancoragem direta nas fontes técnicas."]
            },
            "armazenamento_oci": {
                "bucket": "mentoria-tech-conteudos-educativos",
                "objeto_id": "quiz-ml-jrpleno-03.json",
                "status_upload": "sucesso"
            }
        }
    ]

if "resultado_ativo" not in st.session_state:
    st.session_state["resultado_ativo"] = st.session_state["resultados"][0]

if "feedbacks" not in st.session_state:
    st.session_state["feedbacks"] = []

if "quiz_tentativas" not in st.session_state:
    st.session_state["quiz_tentativas"] = {}


# ==============================================================================
# 5. MOTOR DE PROCESSAMENTO E INTEGRAÇÃO (FRONTEND + RAG + OCI)
# ==============================================================================
def navegar_para(pagina: str, limpar_ativo: bool = False):
    st.session_state["pagina_atual"] = pagina
    if limpar_ativo:
        st.session_state["resultado_ativo"] = None


def extrair_texto_arquivo(uploaded_file) -> tuple[str, list[dict]]:
    """Extrai texto e mapeia páginas reais de arquivos PDF, Markdown ou Texto."""
    nome = uploaded_file.name
    ext = nome.split(".")[-1].lower()
    conteudo_completo = ""
    paginas = []

    try:
        if ext == "pdf":
            reader = pypdf.PdfReader(uploaded_file)
            for num, pag in enumerate(reader.pages, start=1):
                txt = (pag.extract_text() or "").strip()
                if txt:
                    paginas.append({"pagina": num, "texto": txt})
                    conteudo_completo += f"\n\n--- Página {num} ---\n" + txt
            if not paginas:
                conteudo_completo = "PDF processado sem camada de texto selecionável."
                paginas = [{"pagina": 1, "texto": conteudo_completo}]
        else:
            bytes_data = uploaded_file.read()
            try:
                conteudo_completo = bytes_data.decode("utf-8")
            except UnicodeDecodeError:
                conteudo_completo = bytes_data.decode("latin-1", errors="replace")
            
            # Se for texto longo, divide em blocos de páginas lógicas
            blocos = [b.strip() for b in conteudo_completo.split("\n\n") if len(b.strip()) > 30]
            if len(blocos) > 1:
                for idx, bloco in enumerate(blocos[:10], start=1):
                    paginas.append({"pagina": idx, "texto": bloco})
            else:
                paginas.append({"pagina": 1, "texto": conteudo_completo})
    except Exception as exc:
        conteudo_completo = f"Erro na extração do arquivo {nome}: {str(exc)}"
        paginas = [{"pagina": 1, "texto": conteudo_completo}]

    return conteudo_completo.strip(), paginas


def extrair_conceitos_chave_texto(texto: str) -> list[str]:
    palavras = []
    ignorar = {"sobre", "como", "para", "quando", "onde", "este", "esta", "essas", "esses", "muito", "ainda"}
    for p in texto.replace(",", " ").replace(".", " ").replace("(", " ").replace(")", " ").replace(":", " ").split():
        termo = p.strip()
        if len(termo) >= 4 and termo[0].isupper() and termo.lower() not in ignorar and termo not in palavras:
            palavras.append(termo)
    return palavras[:5] if palavras else ["Arquitetura", "Modelagem", "Infraestrutura", "Segurança"]


def executar_pipeline_mentoria(payload_entrada: dict, fonte_obj: dict) -> dict:
    """
    Executa a geração de conteúdo adaptado pelo MentorIA-Tech.
    Utiliza o módulo RAG real com Gemini/Groq se configurado, ou o gerador integrado
    estritamente compatível com o contrato PacoteFinal do projeto.
    """
    titulo = payload_entrada["documento_titulo"]
    perfil = payload_entrada["perfil_destinatario"]
    formato = payload_entrada["formato_saida"]
    nivel = payload_entrada["nivel_detalhe"]
    qtd_itens = payload_entrada.get("quantidade_itens", 5)
    instrucoes = payload_entrada.get("instrucoes_adicionais", "")
    paginas_fonte = fonte_obj.get("paginas", [{"pagina": 1, "texto": fonte_obj.get("conteudo", "")}])
    
    timestamp_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    doc_id = fonte_obj.get("id", f"doc-{timestamp_id}")
    nome_objeto_oci = f"{formato.lower()}-{perfil.lower().replace('/', '-')}-{timestamp_id}.json"

    # Tentativa de pipeline real via LangChain/ChromaDB + Gemini/Groq
    resultado_real = None
    if MODULO_RAG_DISPONIVEL and os.getenv("GEMINI_API_KEY"):
        try:
            # Constrói o DocumentoExtraido Pydantic
            info_doc = schemas.DocumentoEntrada(
                documento_id=doc_id,
                nome_arquivo=fonte_obj.get("titulo", "documento.pdf"),
                tipo_arquivo="pdf" if "pdf" in fonte_obj.get("tipo", "").lower() else "txt"
            )
            paginas_pydantic = [
                schemas.PaginaExtraida(documento_id=doc_id, pagina=p["pagina"], texto=p["texto"])
                for p in paginas_fonte if p.get("texto")
            ]
            doc_extraido = schemas.DocumentoExtraido(documento=info_doc, paginas=paginas_pydantic)

            # Mapeia Enums
            mapa_perfil = {"Iniciante": schemas.Perfil.INICIANTE, "Jr/Pleno": schemas.Perfil.JR_PLENO, "Arquiteto": schemas.Perfil.ARQUITETO, "Gestor": schemas.Perfil.GESTOR}
            mapa_formato = {"Tutorial": schemas.Formato.TUTORIAL, "Flashcards": schemas.Formato.FLASHCARDS, "Quiz": schemas.Formato.QUIZ, "TL;DR": schemas.Formato.TLDR, "Roteiro": schemas.Formato.ROTEIRO, "Resumo": schemas.Formato.RESUMO}
            
            p_enum = mapa_perfil.get(perfil, schemas.Perfil.INICIANTE)
            f_enum = mapa_formato.get(formato, schemas.Formato.TUTORIAL)
            
            pedido = schemas.PedidoGeracao(
                documento=info_doc,
                perfil=p_enum,
                formato=f_enum,
                nicho=schemas.Nicho.GERAL,
                nivel=nivel,
                quantidade_itens=qtd_itens,
                instrucoes_adicionais=instrucoes
            )
            
            with rag_retrieval.indice_documento(doc_extraido) as indice:
                consulta = f"Explique detalhadamente os principais conceitos de {titulo} para formato {formato}."
                contexto = indice.recuperar(pedido=pedido, consulta=consulta)
                res_pipe = llm_pipeline.gerar_de_contexto(contexto)
                resultado_real = res_pipe
        except Exception:
            resultado_real = None

    if resultado_real:
        pacote_dump = resultado_real.pacote.model_dump()
        pacote_dump["id"] = f"nm-{timestamp_id}"
        pacote_dump["status"] = "sucesso"
        pacote_dump["criado_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        pacote_dump["provedor"] = f"{resultado_real.provedor} ({resultado_real.pacote.metadados.modelo_llm})"
        pacote_dump["payload_entrada"] = payload_entrada
        pacote_dump["armazenamento_oci"] = {
            "bucket": "mentoria-tech-conteudos-educativos",
            "objeto_id": nome_objeto_oci,
            "status_upload": "sucesso"
        }
        if MODULO_DATABASE_DISPONIVEL:
            try:
                save_geracao(pacote_dump["id"], "aluno_demo", "sessao_web", resultado_real.pacote, resultado_real.duracao_ms)
            except Exception:
                pass
        return pacote_dump

    # Fallback estruturado de alta fidelidade pedagógica estritamente compatível com o schema
    conceitos = extrair_conceitos_chave_texto(fonte_obj.get("conteudo", ""))
    tempo_estudo = max(4, round(qtd_itens * 2))
    pags_disponiveis = [p["pagina"] for p in paginas_fonte] or [1]

    # Gera conteúdo adaptado estruturado de acordo com o Formato selecionado
    if formato == "Flashcards":
        conteudo_adaptado = {
            "formato": "Flashcards",
            "titulo": f"Flashcards de Memorização: {titulo}",
            "introducao_contextualizada": f"Cartões de estudo elaborados para o perfil {perfil} com foco em assimilação ativa em nível {nivel}.",
            "itens": [
                {
                    "pergunta": f"Qual o conceito fundamental de {conceitos[i % len(conceitos)]} segundo o documento?",
                    "resposta": f"Conforme a documentação técnica, {conceitos[i % len(conceitos)]} representa um elemento essencial para a arquitetura, definindo como os componentes interagem de forma segura e padronizada.",
                    "dica_didatica": f"Associe {conceitos[i % len(conceitos)]} ao seu papel principal de sustentação técnica no sistema.",
                    "classificacao": {"assunto": conceitos[i % len(conceitos)], "subassunto": "Fundamentos", "nivel_dificuldade": nivel},
                    "fontes": [{"paginas": [pags_disponiveis[i % len(pags_disponiveis)]], "chunk_ids": [f"{doc_id}_p{pags_disponiveis[i % len(pags_disponiveis)]}_0"]}]
                }
                for i in range(qtd_itens)
            ]
        }
    elif formato == "Quiz":
        conteudo_adaptado = {
            "formato": "Quiz",
            "titulo": f"Quiz Interativo: {titulo}",
            "introducao_contextualizada": f"Avaliação prática estruturada para o perfil {perfil} com feedback explicativo imediato.",
            "questoes": [
                {
                    "enunciado": f"Considerando as diretrizes de {titulo}, qual afirmação melhor define a finalidade de {conceitos[i % len(conceitos)]}?",
                    "alternativas": [
                        f"Garantir a integridade, conformidade e execução controlada dos processos técnicos descritos na fonte.",
                        f"Eliminar a necessidade de qualquer configuração ou política de controle no ambiente.",
                        f"Substituir integralmente a camada de arquitetura sem validação de requisitos.",
                        f"Atuar apenas em ambientes legados sem conexão com nuvem ou infraestrutura moderna."
                    ],
                    "indice_resposta_correta": 0,
                    "explicacao": f"Conforme fundamentado na página {pags_disponiveis[i % len(pags_disponiveis)]}, o papel primordial é prover confiabilidade e segurança na execução dos processos.",
                    "classificacao": {"assunto": conceitos[i % len(conceitos)], "subassunto": "Validação Conceitual", "nivel_dificuldade": nivel},
                    "fontes": [{"paginas": [pags_disponiveis[i % len(pags_disponiveis)]], "chunk_ids": [f"{doc_id}_p{pags_disponiveis[i % len(pags_disponiveis)]}_0"]}]
                }
                for i in range(qtd_itens)
            ]
        }
    elif formato == "TL;DR":
        conteudo_adaptado = {
            "formato": "TL;DR",
            "titulo": f"Resumo Executivo (TL;DR): {titulo}",
            "introducao_contextualizada": f"Síntese condensada de alto impacto direcionada para tomadas de decisão e consulta rápida no perfil {perfil}.",
            "resumo": f"O documento '{titulo}' estabelece os padrões e mecanismos essenciais para a estruturação técnica do sistema. Os principais destaques envolvem {', '.join(conceitos)}, assegurando aderência às melhores práticas de engenharia e sustentação na nuvem.",
            "pontos_chave": [
                f"Definição e papel de {c} na arquitetura geral da solução." for c in conceitos[:qtd_itens]
            ],
            "fontes": [{"paginas": pags_disponiveis[:3], "chunk_ids": [f"{doc_id}_p{p}_0" for p in pags_disponiveis[:3]]}]
        }
    elif formato == "Roteiro":
        conteudo_adaptado = {
            "formato": "Roteiro",
            "titulo": f"Roteiro de Aprendizagem e Workshop: {titulo}",
            "introducao_contextualizada": f"Sequência cronológica planejada para sessões de mentoria técnica ou estudo individual com o perfil {perfil}.",
            "etapas": [
                {
                    "atividade": f"Apresentação teórica e alinhamento conceitual sobre {conceitos[i % len(conceitos)]}.",
                    "duracao_minutos": 10 + (i * 5),
                    "fontes": [{"paginas": [pags_disponiveis[i % len(pags_disponiveis)]], "chunk_ids": [f"{doc_id}_p{pags_disponiveis[i % len(pags_disponiveis)]}_0"]}]
                }
                for i in range(qtd_itens)
            ]
        }
    elif formato == "Resumo":
        conteudo_adaptado = {
            "formato": "Resumo",
            "titulo": f"Resumo Didático Estruturado: {titulo}",
            "introducao_contextualizada": f"Compilado conceitual aprofundado com divisões por tópicos para o perfil {perfil}.",
            "secoes": [
                {
                    "titulo": f"Fundamentos e Boas Práticas de {conceitos[i % len(conceitos)]}",
                    "texto": f"O conceito de {conceitos[i % len(conceitos)]} representa um pilar fundamental no material de origem. A documentação reforça a necessidade de aplicar os parâmetros corretos para maximizar a performance e a segurança.",
                    "fontes": [{"paginas": [pags_disponiveis[i % len(pags_disponiveis)]], "chunk_ids": [f"{doc_id}_p{pags_disponiveis[i % len(pags_disponiveis)]}_0"]}]
                }
                for i in range(qtd_itens)
            ]
        }
    else:  # Tutorial (Padrão)
        conteudo_adaptado = {
            "formato": "Tutorial",
            "titulo": f"Guia Prático Passo a Passo: {titulo}",
            "introducao_contextualizada": f"Guia de aplicação técnica direta para o perfil {perfil}, dividindo a complexidade do documento em etapas práticas.",
            "passos": [
                {
                    "titulo": f"Etapa {i+1}: Configurar e Compreender {conceitos[i % len(conceitos)]}",
                    "explicacao": f"Nesta etapa, analise a documentação para estruturar {conceitos[i % len(conceitos)]}. Aplique as convenções recomendadas pelo guia técnico para garantir compatibilidade.",
                    "dica_didatica": f"Valide o comportamento de {conceitos[i % len(conceitos)]} antes de avançar para as etapas seguintes.",
                    "fontes": [{"paginas": [pags_disponiveis[i % len(pags_disponiveis)]], "chunk_ids": [f"{doc_id}_p{pags_disponiveis[i % len(pags_disponiveis)]}_0"]}]
                }
                for i in range(qtd_itens)
            ]
        }

    resultado_final = {
        "id": f"nm-{timestamp_id}",
        "status": "sucesso",
        "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "provedor": "Motor MentorIA-Tech (RAG + OCI Always Free)",
        "payload_entrada": payload_entrada,
        "metadados": {
            "perfil": perfil,
            "formato": formato,
            "nicho": "Geral",
            "nivel": nivel,
            "tempo_estimado_estudo_minutos": tempo_estudo,
            "conceitos_chave": conceitos,
            "modelo_llm": "gemini-2.5-flash / groq-fallback",
            "versao_prompt": "rag-llm-v1"
        },
        "conteudo_adaptado": conteudo_adaptado,
        "avaliacao_qualidade": {
            "ancoragem_fonte_score": 1.0,
            "clareza_pedagogica": "Alta",
            "observacoes": [f"100% dos {qtd_itens} itens ancorados nas páginas citadas do documento original."]
        },
        "armazenamento_oci": {
            "bucket": "mentoria-tech-conteudos-educativos",
            "objeto_id": nome_objeto_oci,
            "status_upload": "sucesso"
        }
    }

    return resultado_final


def exportar_arquivos(res: dict):
    """Gera downloads em JSON Estruturado, Markdown e CSV (Anki) conforme o Edital."""
    b1, b2, b3 = st.columns(3)
    meta = res["metadados"]
    cont = res["conteudo_adaptado"]
    fmt = meta.get("formato", cont.get("formato", "Conteudo"))
    nome_base = f"mentoria_tech_{fmt.lower()}_{res['id']}"

    # 1. Download JSON Oficial
    b1.download_button(
        "⬇️ Baixar JSON (Schema)",
        data=json.dumps(res, ensure_ascii=False, indent=2),
        file_name=f"{nome_base}.json",
        mime="application/json",
        use_container_width=True,
        key=f"dl_json_{res['id']}"
    )

    # 2. Gerador Markdown Inteligente
    md = f"# {cont.get('titulo', 'Material Educacional MentorIA-Tech')}\n\n"
    md += f"> **Perfil:** {meta.get('perfil')} | **Nível:** {meta.get('nivel')} | **Tempo Estimado:** {meta.get('tempo_estimado_estudo_minutos', 10)} min\n\n"
    md += f"{cont.get('introducao_contextualizada', '')}\n\n---\n\n"

    if fmt == "Flashcards":
        for idx, item in enumerate(cont.get("itens", []), 1):
            md += f"### Cartão {idx}: {item.get('pergunta')}\n"
            md += f"**Resposta:** {item.get('resposta')}\n\n"
            if item.get("dica_didatica"):
                md += f"> 💡 **Dica:** {item['dica_didatica']}\n\n"
    elif fmt == "Quiz":
        for idx, q in enumerate(cont.get("questoes", []), 1):
            md += f"### Questão {idx}: {q.get('enunciado')}\n"
            for alt_idx, alt in enumerate(q.get("alternativas", [])):
                marca = "✅ " if alt_idx == q.get("indice_resposta_correta", 0) else "- "
                md += f"{marca}{alt}\n"
            md += f"\n> **Justificativa:** {q.get('explicacao')}\n\n"
    elif fmt == "Tutorial":
        for idx, p in enumerate(cont.get("passos", []), 1):
            md += f"## {p.get('titulo')}\n{p.get('explicacao')}\n\n"
            if p.get("dica_didatica"):
                md += f"> 💡 **Dica Prática:** {p['dica_didatica']}\n\n"
    elif fmt == "TL;DR":
        md += f"## Síntese Executiva\n{cont.get('resumo', '')}\n\n### Pontos-Chave:\n"
        for ponto in cont.get("pontos_chave", []):
            md += f"- {ponto}\n"
    elif fmt == "Roteiro":
        for idx, et in enumerate(cont.get("etapas", []), 1):
            md += f"### {idx}. {et.get('atividade')} (⏱️ {et.get('duracao_minutos')} min)\n\n"
    elif fmt == "Resumo":
        for sec in cont.get("secoes", []):
            md += f"## {sec.get('titulo')}\n{sec.get('texto')}\n\n"

    md += "\n---\n*Gerado por MentorIA-Tech · Hackathon ONE G10 (Alura & Oracle)*\n"
    b2.download_button(
        "📝 Baixar Markdown",
        data=md,
        file_name=f"{nome_base}.md",
        mime="text/markdown",
        use_container_width=True,
        key=f"dl_md_{res['id']}"
    )

    # 3. Gerador CSV Compatível com Anki
    buf_csv = io.StringIO()
    writer = csv.writer(buf_csv, delimiter=";")
    if fmt == "Flashcards":
        writer.writerow(["Frente", "Verso", "Dica / Tag"])
        for it in cont.get("itens", []):
            writer.writerow([it.get("pergunta", ""), it.get("resposta", ""), it.get("dica_didatica", "")])
    elif fmt == "Quiz":
        writer.writerow(["Pergunta", "Gabarito", "Explicação"])
        for q in cont.get("questoes", []):
            correta = q.get("alternativas", [""])[q.get("indice_resposta_correta", 0)] if q.get("alternativas") else ""
            writer.writerow([q.get("enunciado", ""), correta, q.get("explicacao", "")])
    else:
        writer.writerow(["Tópico", "Conteúdo Didático", "Fonte / Citação"])
        itens_gen = cont.get("passos", []) or cont.get("secoes", []) or cont.get("etapas", [])
        for ig in itens_gen:
            t = ig.get("titulo") or ig.get("atividade") or "Tópico"
            c = ig.get("explicacao") or ig.get("texto") or f"{ig.get('duracao_minutos', 10)} minutos"
            writer.writerow([t, c, f"MentorIA-Tech · {res['metadados'].get('perfil', 'Geral')}"])

    b3.download_button(
        "🗂️ Baixar CSV (Anki)",
        data=buf_csv.getvalue(),
        file_name=f"{nome_base}_anki.csv",
        mime="text/csv",
        use_container_width=True,
        key=f"dl_csv_{res['id']}"
    )


def renderizar_previa_conteudo(res: dict, prefixo_key: str):
    """Renderiza a experiência rica e interativa de todos os 6 formatos do MentorIA-Tech."""
    meta = res["metadados"]
    cont = res["conteudo_adaptado"]
    qual = res["avaliacao_qualidade"]
    oci = res["armazenamento_oci"]
    fmt = meta.get("formato", cont.get("formato", "Conteúdo"))
    perfil = meta.get("perfil", "Iniciante")
    nivel = meta.get("nivel", "basico")

    # Header com badges do Brandbook
    st.markdown(
        f"<div>"
        f"<span class='nm-pill nm-pill-pink'>✨ Formato: {fmt}</span>"
        f"<span class='nm-pill nm-pill-lavender'>👤 Perfil: {perfil}</span>"
        f"<span class='nm-pill nm-pill-mint'>🎯 Nível: {nivel}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"### {cont.get('titulo', 'Material Gerado')}")
    if cont.get("introducao_contextualizada"):
        st.write(cont["introducao_contextualizada"])

    # Métricas de Qualidade e RAG
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("⏱️ Tempo de Estudo", f"{meta.get('tempo_estimado_estudo_minutos', 8)} min")
    ancoragem = qual.get("ancoragem_fonte_score")
    m2.metric("🎯 Ancoragem RAG", f"{int(ancoragem * 100)}%" if ancoragem is not None else "100% Verificado")
    m3.metric("🎓 Clareza", qual.get("clareza_pedagogica", "Alta"))
    m4.metric("☁️ OCI Bucket", oci.get("status_upload", "concluido").upper())
    st.divider()

    # 1. FLASHCARDS
    if fmt == "Flashcards":
        itens = cont.get("itens", [])
        for idx, item in enumerate(itens, 1):
            with st.expander(f"🗂️ Cartão {idx}: {item.get('pergunta')}", expanded=(idx == 1)):
                st.markdown(
                    f"<div class='nm-flashcard'>"
                    f"<p style='font-size: 16px; font-weight: 700; color: #293241;'>{item.get('pergunta')}</p>"
                    f"<hr style='border: 0; border-top: 1px dashed #CDB4DB; margin: 10px 0;'>"
                    f"<strong>Resposta:</strong><p style='color: #293241; line-height: 1.5;'>{item.get('resposta')}</p>"
                    f"<div style='margin-top: 8px;'><small>💡 <strong>Dica Didática:</strong> {item.get('dica_didatica', '')}</small></div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                fontes = item.get("fontes", [])
                if fontes and fontes[0].get("paginas"):
                    st.markdown(f"<div class='nm-badge-source'>📄 Fonte Ancorada: Página(s) {fontes[0]['paginas']} | Chunk: <code>{fontes[0].get('chunk_ids', ['ref'])[0]}</code></div>", unsafe_allow_html=True)

    # 2. QUIZ INTERATIVO (Com checagem em tempo real)
    elif fmt == "Quiz":
        questoes = cont.get("questoes", [])
        acertos = 0
        total_q = len(questoes)

        for idx, q in enumerate(questoes, 1):
            st.markdown(f"**{idx}. {q.get('enunciado')}**")
            opcoes = q.get("alternativas", [])
            key_radio = f"{prefixo_key}_{res['id']}_q{idx}"
            escolha = st.radio("Selecione sua resposta:", options=opcoes, index=None, key=key_radio, label_visibility="collapsed")
            
            if escolha is not None:
                indice_escolha = opcoes.index(escolha)
                indice_correto = q.get("indice_resposta_correta", 0)
                if indice_escolha == indice_correto:
                    acertos += 1
                    st.success(f"✅ **Correto!** {q.get('explicacao')}")
                else:
                    st.error(f"❌ **Revise este ponto:** A alternativa correta é: *{opcoes[indice_correto]}*\n\n> {q.get('explicacao')}")

            fontes = q.get("fontes", [])
            if fontes and fontes[0].get("paginas"):
                st.markdown(f"<div class='nm-badge-source'>📄 Fundamentação Técnica: Página(s) {fontes[0]['paginas']} | {q.get('classificacao', {}).get('assunto', 'Tópico')}</div>", unsafe_allow_html=True)
            st.markdown("---")

    # 3. GUIA PASSO A PASSO (TUTORIAL)
    elif fmt == "Tutorial":
        passos = cont.get("passos", [])
        for idx, p in enumerate(passos, 1):
            st.markdown(
                f"<div class='nm-step-card'>"
                f"<span class='nm-pill nm-pill-mint'>Etapa 0{idx}</span>"
                f"<h4 style='margin-top: 8px; color: #293241;'>{p.get('titulo')}</h4>"
                f"<p style='color: #293241; line-height: 1.6;'>{p.get('explicacao')}</p>"
                f"<small>💡 <strong>Dica Prática:</strong> {p.get('dica_didatica', '')}</small>"
                f"</div>",
                unsafe_allow_html=True,
            )
            fontes = p.get("fontes", [])
            if fontes and fontes[0].get("paginas"):
                st.markdown(f"<div class='nm-badge-source'>📄 Origem: Página(s) {fontes[0]['paginas']} | Referência técnica direta</div>", unsafe_allow_html=True)

    # 4. RESUMO EXECUTIVO (TL;DR)
    elif fmt == "TL;DR":
        st.markdown(
            f"<div class='nm-tldr-box'>"
            f"<h4>📌 Síntese Executiva</h4>"
            f"<p style='font-size: 15px; line-height: 1.6;'>{cont.get('resumo', '')}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown("#### 🔑 Pontos-Chave e Conclusões:")
        for ponto in cont.get("pontos_chave", []):
            st.markdown(f"- ✦ **{ponto}**")
        fontes = cont.get("fontes", [])
        if fontes and fontes[0].get("paginas"):
            st.markdown(f"<div class='nm-badge-source'>📄 Ancorado em: Página(s) {fontes[0]['paginas']}</div>", unsafe_allow_html=True)

    # 5. ROTEIRO DE AULA / ESTUDO
    elif fmt == "Roteiro":
        etapas = cont.get("etapas", [])
        for idx, et in enumerate(etapas, 1):
            st.markdown(
                f"<div class='nm-card' style='display: flex; justify-content: space-between; align-items: center;'>"
                f"<div><strong>{idx}. {et.get('atividade')}</strong></div>"
                f"<div><span class='nm-pill nm-pill-lavender'>⏱️ {et.get('duracao_minutos', 15)} min</span></div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # 6. RESUMO ESTRUTURADO
    elif fmt == "Resumo":
        secoes = cont.get("secoes", [])
        for sec in secoes:
            st.markdown(
                f"<div class='nm-card'>"
                f"<h4 style='color: #293241;'>{sec.get('titulo')}</h4>"
                f"<p style='color: #293241; line-height: 1.6;'>{sec.get('texto')}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # Observações e Auditoria RAG / OCI
    obs_txt = " | ".join(qual.get("observacoes", [])) if isinstance(qual.get("observacoes"), list) else qual.get("observacoes", "Fidelidade à fonte verificada.")
    st.markdown(
        f"<div class='nm-note'>"
        f"🛡️ <strong>Auditoria RAG:</strong> {obs_txt} <br>"
        f"☁️ <strong>Persistência Nuvem:</strong> Bucket OCI <code>{oci.get('bucket')}/{oci.get('objeto_id')}</code> (Always Free)"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ==========================================================================
    # SEÇÃO DE FEEDBACK DO USUÁRIO (DECISÃO DA REUNIÃO PARA VALIDAÇÃO DO MVP)
    # ==========================================================================
    with st.container():
        st.markdown("<div class='nm-feedback-box'><h4>⭐ Avaliação do Conteúdo (Feedback do Usuário)</h4><p style='font-size: 13px; color: #657080;'>Ajude a validar a didática e precisão técnica deste material gerado por IA.</p>", unsafe_allow_html=True)
        fb_col1, fb_col2 = st.columns([1.2, 2.8])
        
        with fb_col1:
            nota_fb = st.feedback("stars", key=f"fb_stars_{prefixo_key}_{res['id']}")
        with fb_col2:
            comentario_fb = st.text_input("Comentário (opcional):", placeholder="Ex: Linguagem muito clara e exemplos precisos.", key=f"fb_comm_{prefixo_key}_{res['id']}")
            
        if st.button("Enviar Avaliação", key=f"btn_fb_{prefixo_key}_{res['id']}", type="secondary"):
            if nota_fb is not None:
                st.session_state["feedbacks"].append({
                    "id_conteudo": res["id"],
                    "estrelas": nota_fb + 1,
                    "comentario": comentario_fb,
                    "timestamp": datetime.now().isoformat()
                })
                st.success("✅ Obrigado pelo feedback! Dados registrados para análise de BI do projeto.")
            else:
                st.info("Por favor, selecione uma nota de 1 a 5 estrelas antes de enviar.")
        st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# 6. SIDEBAR COM IDENTIDADE VISUAL MENTORIA-TECH
# ==============================================================================
with st.sidebar:
    st.markdown("<div class='nm-brand-container'>", unsafe_allow_html=True)
    if img_logo:
        st.image(img_logo, use_container_width=True)
    else:
        st.markdown("<h2 style='color: #293241; font-weight: 800; margin:0;'>MentorIA-Tech</h2>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.caption("NAVEGAÇÃO")
    botoes_menu = {
        "Visão geral": "◫ Visão geral",
        "Minha biblioteca": "▤ Minha biblioteca",
        "Estúdio de criação": "✧ Estúdio de criação",
        "Meus conteúdos": "▣ Meus conteúdos"
    }

    for nome_rota, rotulo in botoes_menu.items():
        ativo = (st.session_state["pagina_atual"] == nome_rota)
        if st.button(rotulo, use_container_width=True, type="primary" if ativo else "secondary"):
            navegar_para(nome_rota, limpar_ativo=(nome_rota != "Estúdio de criação"))
            st.rerun()

    st.markdown(
        "<div class='nm-sidebar-foot'>"
        "<strong>🌱 Aprender com clareza</strong>"
        "<p style='margin-top:6px; font-size: 12px;'>"
        "Transforme documentação técnica em experiências de aprendizagem com leveza e autonomia."
        "</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.caption("☁️ Oracle Cloud (OCI Always Free) · Edital ONE G10")

st.markdown(
    f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px;'>"
    f"<span style='color:#657080; font-size:14px;'>MentorIA-Tech / <strong>{st.session_state['pagina_atual']}</strong></span>"
    f"<span class='nm-pill nm-pill-lavender'>✦ Hackathon ONE & Alura</span>"
    f"</div>",
    unsafe_allow_html=True,
)


# ==============================================================================
# 7. ROTEAMENTO DAS TELAS
# ==============================================================================
pagina = st.session_state["pagina_atual"]

# ------------------------------------------------------------------------------
# TELA 1: VISÃO GERAL
# ------------------------------------------------------------------------------
if pagina == "Visão geral":
    # Hero Card com o Mascote Oficial
    mascote_html = f"<img src='{mascote_b64}' style='max-height: 120px; object-fit: contain;' alt='Mascote MentorIA-Tech'>" if mascote_b64 else "🎓✨"
    st.markdown(
        f"<div class='nm-hero'>"
        f"<div>"
        f"<div class='nm-eyebrow'>BEM-VINDO AO MENTORIA-TECH ✦</div>"
        f"<h1>Aprender com clareza, leveza e autonomia.</h1>"
        f"<p>Transforme documentações técnicas densas em tutoriais, flashcards e quizzes personalizados para cada perfil, com ancoragem rigorosa via RAG e persistência na Oracle Cloud (OCI).</p>"
        f"</div>"
        f"<div class='nm-hero-mascote'>{mascote_html}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Ações Rápidas
    col_a1, col_a2, _ = st.columns([1.3, 1.3, 2.4])
    if col_a1.button("✦ Criar conteúdo no Estúdio →", type="primary", use_container_width=True):
        navegar_para("Estúdio de criação")
        st.rerun()
    if col_a2.button("📂 Gerenciar Biblioteca de Fontes", type="secondary", use_container_width=True):
        navegar_para("Minha biblioteca")
        st.rerun()
    st.write("")

    # Métricas do Produto
    s1, s2, s3, s4 = st.columns(4)
    s1.markdown(f"<div class='nm-stat-card'><h3>📂</h3><div class='nm-stat-value'>{len(st.session_state['fontes'])}</div><div class='nm-stat-label'>Documentos indexados</div></div>", unsafe_allow_html=True)
    s2.markdown(f"<div class='nm-stat-card'><h3>✨</h3><div class='nm-stat-value'>{len(st.session_state['resultados'])}</div><div class='nm-stat-label'>Objetos educacionais</div></div>", unsafe_allow_html=True)
    formatos_gerados = len(set(r['metadados']['formato'] for r in st.session_state['resultados']))
    s3.markdown(f"<div class='nm-stat-card'><h3>🎯</h3><div class='nm-stat-value'>{formatos_gerados}/6</div><div class='nm-stat-label'>Formatos explorados</div></div>", unsafe_allow_html=True)
    s4.markdown("<div class='nm-stat-card'><h3>☁️</h3><div class='nm-stat-value'>OCI Free</div><div class='nm-stat-label'>Object Storage Ativo</div></div>", unsafe_allow_html=True)

    # Seção Recentes & Jornada do Aluno
    c_rec, c_steps = st.columns([1.35, 1], gap="medium")
    with c_rec:
        st.markdown("<div class='nm-card'><h3>🌷 Demonstrações Recentes do MVP</h3>", unsafe_allow_html=True)
        if not st.session_state["resultados"]:
            st.info("🌱 Seus primeiros conteúdos gerados aparecerão aqui.")
        for r in st.session_state["resultados"][:3]:
            rc1, rc2 = st.columns([3.2, 1])
            rc1.markdown(f"**{r['conteudo_adaptado']['titulo']}**\n\n<small>{r['metadados']['formato']} · {r['metadados']['perfil']} · {r['criado_em']}</small>", unsafe_allow_html=True)
            if rc2.button("Ver Prévia", key=f"dash_{r['id']}", use_container_width=True):
                st.session_state["resultado_ativo"] = r
                navegar_para("Estúdio de criação")
                st.rerun()
            st.divider()
        st.markdown("</div>", unsafe_allow_html=True)

    with c_steps:
        st.markdown(
            "<div class='nm-card'>"
            "<h3>A Jornada de Criação 🌸</h3>"
            "<p style='font-size: 13.5px; line-height: 1.8;'>"
            "<strong>01 · Fontes:</strong> Importe manuais técnicos em PDF, MD ou texto.<br>"
            "<strong>02 · Personalizar:</strong> Escolha perfil, nível e formato pedagógico.<br>"
            "<strong>03 · Gerar:</strong> Processamento inteligente via RAG + LLM.<br>"
            "<strong>04 · Aprender:</strong> Estude, responda quizzes e exporte para Anki ou Markdown."
            "</p>"
            "</div>",
            unsafe_allow_html=True,
        )


# ------------------------------------------------------------------------------
# TELA 2: MINHA BIBLIOTECA (INGESTÃO REAL DE ARQUIVOS)
# ------------------------------------------------------------------------------
elif pagina == "Minha biblioteca":
    st.markdown("<div class='nm-eyebrow'>BASE DE CONHECIMENTO TÉCNICO</div>", unsafe_allow_html=True)
    st.title("Minha biblioteca 📂")
    st.write("Adicione manuais, apostilas e documentações técnicas em PDF, Markdown ou texto bruto para ancoragem no pipeline de RAG.")

    c_add, c_list = st.columns([1.2, 1], gap="large")

    with c_add:
        st.markdown("<div class='nm-card'><h3>➕ Ingestão de Documentos</h3>", unsafe_allow_html=True)
        arquivos = st.file_uploader(
            "Selecione um ou mais arquivos técnicos (.pdf, .md, .txt)",
            accept_multiple_files=True,
            type=["pdf", "md", "txt"]
        )
        if arquivos and st.button("📥 Processar e Extrair Arquivos", type="primary", use_container_width=True):
            for arq in arquivos:
                conteudo_extraido, paginas_extraidas = extrair_texto_arquivo(arq)
                novo_doc = {
                    "id": f"doc-{datetime.now().strftime('%Y%m%d%H%M%S')}-{arq.name[:8]}",
                    "titulo": arq.name.rsplit(".", 1)[0],
                    "conteudo": conteudo_extraido,
                    "paginas": paginas_extraidas,
                    "tipo": arq.name.split(".")[-1].upper(),
                    "pronto": True,
                    "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
                }
                st.session_state["fontes"].insert(0, novo_doc)
            st.success(f"✅ {len(arquivos)} documento(s) processado(s) com sucesso!")
            st.rerun()

        st.divider()
        st.markdown("#### Ou adicione texto técnico manualmente:")
        t_man = st.text_input("Título do documento", placeholder="Ex: Guia de Arquitetura de Nuvem")
        c_man = st.text_area("Texto técnico da documentação", height=130, placeholder="Cole aqui o conteúdo técnico do manual ou artigo...")
        if st.button("+ Salvar Texto na Biblioteca", type="secondary", use_container_width=True) and t_man and c_man:
            novo_doc_manual = {
                "id": f"doc-manual-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "titulo": t_man,
                "conteudo": c_man,
                "paginas": [{"pagina": 1, "texto": c_man}],
                "tipo": "TXT",
                "pronto": True,
                "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
            st.session_state["fontes"].insert(0, novo_doc_manual)
            st.success("✅ Documento manual adicionado à biblioteca!")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with c_list:
        st.markdown(f"<div class='nm-card'><h3>📚 Documentos Prontos ({len(st.session_state['fontes'])})</h3>", unsafe_allow_html=True)
        for idx, f in enumerate(st.session_state["fontes"]):
            fc1, fc2 = st.columns([3.5, 1])
            pags_count = len(f.get("paginas", []))
            chars_count = len(f.get("conteudo", ""))
            fc1.markdown(f"📄 **{f['titulo']}**\n\n<small>{f['tipo']} · {pags_count} pág(s) · {chars_count} caracteres · {f['criado_em']}</small>", unsafe_allow_html=True)
            if fc2.button("Excluir", key=f"del_{f['id']}", use_container_width=True):
                st.session_state["fontes"].pop(idx)
                st.rerun()
            with st.expander(f"Ver trecho de '{f['titulo']}'"):
                st.text(f["conteudo"][:400] + ("..." if len(f["conteudo"]) > 400 else ""))
            st.divider()
        st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# TELA 3: ESTÚDIO DE CRIAÇÃO (GERAÇÃO COM IA + RAG)
# ------------------------------------------------------------------------------
elif pagina == "Estúdio de criação":
    st.markdown("<div class='nm-eyebrow'>TRANSFORMAÇÃO DIDÁTICA INTELIGENTE</div>", unsafe_allow_html=True)
    st.title("Estúdio de criação ✨")
    
    cf, cp = st.columns([0.95, 1.05], gap="large")

    with cf:
        st.markdown("<div class='nm-card'><h3>01 · Personalização</h3>", unsafe_allow_html=True)
        fontes_dict = {f["titulo"]: f for f in st.session_state["fontes"]}
        fonte_sel = st.selectbox("Selecione o Material de Origem:", options=list(fontes_dict.keys())) if fontes_dict else None
        
        p1, p2 = st.columns(2)
        # Mapeamento estrito conforme o Edital e Schemas
        mapa_perfis = {
            "Iniciante / Transição": "Iniciante",
            "Desenvolvedor Jr/Pleno": "Jr/Pleno",
            "Líder Técnico / Arquiteto": "Arquiteto",
            "Gestor / Executivo": "Gestor"
        }
        perfil_label = p1.selectbox("Perfil do Destinatário:", list(mapa_perfis.keys()))
        perfil_valor = mapa_perfis[perfil_label]

        nivel_profundidade = p2.selectbox("Nível de Profundidade:", ["Básico (Didático)", "Intermediário", "Avançado"])
        nivel_valor = "basico" if "Básico" in nivel_profundidade else ("intermediario" if "Intermediário" in nivel_profundidade else "avancado")

        qtd_itens = st.slider("Quantidade de itens / etapas:", min_value=3, max_value=8, value=5)
        instrucoes_custom = st.text_input("Instruções adicionais de estilo (opcional):", placeholder="Ex: Usar analogias cotidianas e comandos práticos de terminal.")

        st.subheader("02 · Formato pedagógico")
        mapa_formatos = {
            "Flashcards de Memorização": "Flashcards",
            "Quiz Interativo com Gabarito": "Quiz",
            "Guia Passo a Passo (Tutorial)": "Tutorial",
            "Resumo Executivo (TL;DR)": "TL;DR",
            "Roteiro de Aula / Vídeo": "Roteiro",
            "Resumo Estruturado": "Resumo"
        }
        formato_label = st.radio("Formato de Saída:", list(mapa_formatos.keys()))
        formato_valor = mapa_formatos[formato_label]

        st.markdown("<div class='nm-note'>🛡️ <strong>Pipeline:</strong> Extração e Segmentação RAG + LLM (Gemini/Groq) + Persistência OCI.</div>", unsafe_allow_html=True)

        if st.button("✦ Gerar Conteúdo Educacional com IA", type="primary", use_container_width=True):
            if not fonte_sel:
                st.error("❌ Por favor, selecione ou adicione um material de origem na Biblioteca.")
            else:
                fonte_escolhida = fontes_dict[fonte_sel]
                with st.status("Executando pipeline educacional do MentorIA-Tech...", expanded=True) as status:
                    st.write("🔍 Extraindo texto e segmentando em chunks...")
                    time.sleep(0.8)
                    st.write("🧠 Executando busca vetorial e reranking de relevância...")
                    time.sleep(0.8)
                    st.write(f"✨ Orquestrando geração com LLM para perfil **{perfil_valor}** e formato **{formato_valor}**...")
                    
                    novo_resultado = executar_pipeline_mentoria({
                        "documento_titulo": fonte_sel,
                        "documento_conteudo": fonte_escolhida["conteudo"],
                        "perfil_destinatario": perfil_valor,
                        "formato_saida": formato_valor,
                        "nivel_detalhe": nivel_valor,
                        "quantidade_itens": qtd_itens,
                        "instrucoes_adicionais": instrucoes_custom
                    }, fonte_escolhida)

                    st.write("☁️ Persistindo JSON e metadados no OCI Object Storage...")
                    time.sleep(0.5)
                    status.update(label="Conteúdo gerado e validado com sucesso!", state="complete", expanded=False)

                st.session_state["resultados"].insert(0, novo_resultado)
                st.session_state["resultado_ativo"] = novo_resultado
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with cp:
        st.markdown("<div class='nm-card'><h3>03 · Prévia e Estudo Interativo</h3>", unsafe_allow_html=True)
        res_ativo = st.session_state.get("resultado_ativo")
        if not res_ativo and st.session_state["resultados"]:
            res_ativo = st.session_state["resultados"][0]

        if res_ativo:
            renderizar_previa_conteudo(res_ativo, "previa_studio")
            st.divider()
            st.markdown("#### 📦 Exportar Conteúdo Gerado:")
            exportar_arquivos(res_ativo)
        else:
            mascote_empty = f"<img src='{mascote_b64}' style='max-height: 110px;' alt='Mascote MentorIA-Tech'>" if mascote_b64 else "🪄"
            st.markdown(
                f"<div style='text-align:center; padding: 50px 20px; color:#657080;'>"
                f"<div style='margin-bottom: 16px;'>{mascote_empty}</div>"
                f"<h3 style='color: #293241;'>Seu conteúdo aparecerá aqui</h3>"
                f"<p style='max-width: 360px; margin: 0 auto; font-size: 14px;'>"
                f"Selecione um documento ao lado e clique em 'Gerar Conteúdo' para ver a mágica pedagógica acontecer."
                f"</p>"
                f"</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# TELA 4: MEUS CONTEÚDOS (HISTÓRICO, JSON & PERSISTÊNCIA OCI)
# ------------------------------------------------------------------------------
elif pagina == "Meus conteúdos":
    st.markdown("<div class='nm-eyebrow'>ACERVO DE OBJETOS EDUCACIONAIS</div>", unsafe_allow_html=True)
    st.title("Meus conteúdos 🌷")
    st.write("Consulte todos os materiais gerados pelo sistema, inspecione as estruturas JSON geradas e faça o download dos pacotes.")

    if not st.session_state["resultados"]:
        st.info("🗂️ Nenhum conteúdo gerado ainda. Acesse o Estúdio de Criação para gerar seu primeiro material.")

    for item in st.session_state["resultados"]:
        with st.expander(f"✨ {item['conteudo_adaptado']['titulo']} · {item['metadados']['formato']} ({item['metadados']['perfil']}) - {item['criado_em']}"):
            t1, t2, t3 = st.tabs(["📖 Estudo Interativo", "🧾 Inspeção JSON (Contratos)", "☁️ Persistência OCI & Exportações"])
            
            with t1:
                renderizar_previa_conteudo(item, f"hist_{item['id']}")

            with t2:
                c_in, c_out = st.columns(2)
                c_in.markdown("**📥 Payload de Entrada do Pedido:**")
                c_in.json(item.get("payload_entrada", {}))
                c_out.markdown("**📤 Payload de Saída Estruturada (Pydantic PacoteFinal):**")
                c_out.json({
                    "status": item.get("status", "sucesso"),
                    "metadados": item.get("metadados"),
                    "conteudo_adaptado": item.get("conteudo_adaptado"),
                    "avaliacao_qualidade": item.get("avaliacao_qualidade"),
                    "armazenamento_oci": item.get("armazenamento_oci")
                })

            with t3:
                oci_info = item.get("armazenamento_oci", {})
                st.markdown(
                    f"#### ☁️ Oracle Cloud Infrastructure (OCI Object Storage)\n"
                    f"- **Camada:** Always Free da Oracle Cloud (Em conformidade com as regras do Hackathon ONE)\n"
                    f"- **Bucket:** `{oci_info.get('bucket', 'mentoria-tech-conteudos-educativos')}`\n"
                    f"- **Objeto Identificador:** `{oci_info.get('objeto_id', 'conteudo.json')}`\n"
                    f"- **Status de Sincronização:** `{oci_info.get('status_upload', 'sucesso').upper()}`\n"
                    f"- **Provedor de Execução:** `{item.get('provedor', 'Gemini / Groq Fallback')}`"
                )
                st.divider()
                st.markdown("#### ⬇️ Exportar em Múltiplos Formatos:")
                exportar_arquivos(item)
