"""Suíte de Testes de QA, Contratos e Integridade do Pipeline — MentorIA Tech (Equipe 26).

Testes automatizados com pytest e unittest.mock / FastAPI TestClient.
NENHUMA chamada real de API externa ou OCI é executada aqui — execução 100% isolada.

Executar:
    pytest tests/test_qa_pipeline.py -v
"""

import json
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

# Garante que a raiz do projeto e rag/ estejam no sys.path para imports
_ROOT = Path(__file__).parent.parent
_RAG = _ROOT / "rag"
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if str(_RAG) not in sys.path:
    sys.path.insert(0, str(_RAG))

from pipeline.schemas import (
    ArmazenamentoOCI,
    AvaliacaoQualidade,
    Classificacao,
    ContextoRAG,
    Dificuldade,
    DocumentoEntrada,
    DocumentoExtraido,
    Flashcard,
    Flashcards,
    Fonte,
    Formato,
    Metadados,
    PacoteFinal,
    PaginaExtraida,
    PedidoGeracao,
    Perfil,
    QuestaoQuiz,
    Quiz,
    TrechoRecuperado,
)


def _fonte_exemplo(chunk_id: str = "doc_ml_p1_0", paginas: list[int] | None = None) -> Fonte:
    return Fonte(paginas=paginas or [1], chunk_ids=[chunk_id])


def _classificacao_exemplo(nivel: Dificuldade = Dificuldade.BASICO) -> Classificacao:
    return Classificacao(assunto="Machine Learning", subassunto="Conceitos", nivel_dificuldade=nivel)


# ==============================================================================
# BLOCO 1: SCHEMAS E CONTRATOS DE DADOS (PYDANTIC V2)
# ==============================================================================

def test_01_schema_documento_valido():
    """Cenário 1: Validação de documento de entrada com campos válidos."""
    doc = DocumentoEntrada(
        documento_id="doc_ml_01",
        nome_arquivo="Machine_Learning.pdf",
        tipo_arquivo="pdf",
    )
    assert doc.documento_id == "doc_ml_01"
    assert doc.tipo_arquivo == "pdf"


def test_02_schema_documento_invalido_rejeita_campos_extras():
    """Cenário 2: Validação estrita (extra='forbid') rejeita campos não declarados."""
    with pytest.raises(ValidationError):
        DocumentoEntrada(
            documento_id="doc_01",
            nome_arquivo="doc.pdf",
            campo_invalido_hacker="tentativa_injecao",
        )


def test_03_schema_pedido_geracao_perfis_e_formatos():
    """Cenário 3: Pedido de geração aceita os perfis oficiais sem campo Nicho."""
    doc = DocumentoEntrada(documento_id="doc_01", nome_arquivo="Machine_Learning.pdf")
    assert [p.value for p in Perfil] == ["Iniciante", "Jr/Pleno", "Tech Lead", "Gestor"]

    pedido = PedidoGeracao(
        documento=doc,
        perfil=Perfil.ARQUITETO,
        formato=Formato.FLASHCARDS,
        nivel="basico",
        quantidade_itens=5,
    )
    assert pedido.perfil.value == "Tech Lead"
    assert pedido.formato.value == "Flashcards"
    assert pedido.quantidade_itens == 5


def test_04_schema_conteudo_flashcards_valido():
    """Cenário 4: Validação de estrutura de Flashcards com fontes rastreáveis."""
    card = Flashcard(
        pergunta="O que é Overfitting?",
        resposta="Quando o modelo decora os dados de treino e erra em novos dados.",
        classificacao=_classificacao_exemplo(),
        fontes=[_fonte_exemplo("doc_ml_p1_0", [1, 2])],
    )
    fc = Flashcards(formato="Flashcards", itens=[card])
    assert fc.formato == "Flashcards"
    assert len(fc.itens) == 1
    assert fc.itens[0].fontes[0].chunk_ids == ["doc_ml_p1_0"]


def test_05_schema_quiz_rejeita_alternativas_duplicadas():
    """Cenário 5: QA de integridade — Quiz deve rejeitar alternativas duplicadas."""
    with pytest.raises(ValidationError) as exc:
        QuestaoQuiz(
            enunciado="Qual métrica avalia classificação?",
            alternativas=["Acurácia", "Acurácia", "F1-Score"],
            indice_resposta_correta=0,
            explicacao="Acurácia mede proporção de acertos.",
            classificacao=_classificacao_exemplo(),
            fontes=[_fonte_exemplo("doc_ml_p3_0", [3])],
        )
    assert "Alternativas duplicadas" in str(exc.value)


def test_06_schema_pacote_final_consistencia_formato():
    """Cenário 6: QA de coerência — Metadados e ConteúdoAdaptado devem ter mesmo formato."""
    meta = Metadados(
        documento_id="doc_01",
        perfil=Perfil.INICIANTE,
        formato=Formato.FLASHCARDS,
        nivel="basico",
        tempo_estimado_estudo_minutos=10,
    )
    quiz = Quiz(
        formato="Quiz",
        questoes=[
            QuestaoQuiz(
                enunciado="Pergunta?",
                alternativas=["A", "B"],
                indice_resposta_correta=0,
                explicacao="Exp",
                classificacao=_classificacao_exemplo(),
                fontes=[_fonte_exemplo()],
            )
        ],
    )
    with pytest.raises(ValidationError) as exc:
        PacoteFinal(
            metadados=meta,
            conteudo_adaptado=quiz,
            avaliacao_qualidade=AvaliacaoQualidade(),
            armazenamento_oci=ArmazenamentoOCI(status_upload="pendente"),
        )
    assert "Formato dos metadados difere do conteúdo" in str(exc.value)


def test_07_schema_armazenamento_oci_sucesso_exige_bucket_e_objeto():
    """Cenário 7: ArmazenamentoOCI com status 'sucesso' exige bucket e objeto_id preenchidos."""
    with pytest.raises(ValidationError) as exc:
        ArmazenamentoOCI(status_upload="sucesso", bucket=None, objeto_id=None)
    assert "Upload concluído requer bucket e objeto_id" in str(exc.value)


# ==============================================================================
# BLOCO 2: GESTÃO DE SEGREDOS E POOL DE CHAVES (SERVICES)
# ==============================================================================

def test_08_oci_secrets_pool_rotation(monkeypatch):
    """Cenário 8: Pool de rotação alterna entre chaves disponíveis (Round-Robin)."""
    from itertools import cycle
    from services import oci_secrets

    monkeypatch.setenv("GEMINI_API_KEYS", "chave_alpha,chave_beta")
    pool = oci_secrets._carregar_pool("GEMINI_API_KEYS", "GEMINI_API_KEY")
    monkeypatch.setattr(oci_secrets, "_ciclo_gemini", cycle(pool))

    assert oci_secrets.obter_chave_gemini() == "chave_alpha"
    assert oci_secrets.obter_chave_gemini() == "chave_beta"
    assert oci_secrets.obter_chave_gemini() == "chave_alpha"


def test_09_oci_secrets_fallback_chave_unica(monkeypatch):
    """Cenário 9: oci_secrets funciona tanto com chave única quanto com lista plural."""
    from itertools import cycle
    from services import oci_secrets

    monkeypatch.setenv("GEMINI_API_KEY", "chave_unica_123")
    monkeypatch.delenv("GEMINI_API_KEYS", raising=False)
    pool = oci_secrets._carregar_pool("GEMINI_API_KEYS", "GEMINI_API_KEY")
    monkeypatch.setattr(oci_secrets, "_ciclo_gemini", cycle(pool))

    assert oci_secrets.obter_chave_gemini() == "chave_unica_123"


# ==============================================================================
# BLOCO 3: STORAGE OCI E RESILIÊNCIA A FALHAS (SERVICES)
# ==============================================================================

def test_10_oci_storage_upload_sucesso_mock():
    """Cenário 10: Upload OCI concluído com sucesso retorna metadados conformes."""
    from services import oci_storage

    payload = {"teste": "dados_de_mentoria"}
    mock_cliente = MagicMock()
    mock_cliente.put_object.return_value = MagicMock(status=200)

    with patch("services.oci_storage._obter_cliente_e_namespace", return_value=(mock_cliente, "grclodnfw2hl")):
        resultado = oci_storage._tentar_upload_oci(payload, "resultado_demo.json")

    assert resultado["bucket"] == "mentoria-tech-artifacts"
    assert resultado["objeto_id"] == "resultado_demo.json"
    assert resultado["status_upload"] == "concluido"
    mock_cliente.put_object.assert_called_once()


def test_11_oci_storage_fallback_local_quando_sem_oci(tmp_path, monkeypatch):
    """Cenário 11: Se OCI indisponível, salva localmente em data/oci_fallback/."""
    from services import oci_storage

    monkeypatch.setattr(oci_storage, "_PASTA_FALLBACK", tmp_path)
    payload = {"aluno": "Lidia", "status": "qa_sucesso"}

    resultado = oci_storage._salvar_localmente(payload, "resultado_offline.json")

    assert resultado["status_upload"] == "fallback_local"
    assert (tmp_path / "resultado_offline.json").exists()


# ==============================================================================
# BLOCO 4: EXPORTADOR DE BI PARA POWER BI (SERVICES)
# ==============================================================================

def test_12_bi_exporter_exportacao_csv(tmp_path, monkeypatch):
    """Cenário 12: Exportador de BI lê SQLite e gera CSV sanitizado sem JSONs brutos."""
    from services import bi_exporter

    db_file = tmp_path / "teste_novamente.db"
    con = sqlite3.connect(str(db_file))
    con.execute(
        "CREATE TABLE geracoes (id TEXT, documento_id TEXT, perfil TEXT, formato TEXT, data_hora TEXT, pacote_json TEXT)"
    )
    con.execute(
        "INSERT INTO geracoes VALUES ('gen_1', 'doc_ml', 'Iniciante', 'Flashcards', '2026-11-12T15:00:00Z', '{\"a\":1}')"
    )
    con.commit()
    con.close()

    export_dir = tmp_path / "exports"
    monkeypatch.setattr(bi_exporter, "_DB_PATH", db_file)
    monkeypatch.setattr(bi_exporter, "_PASTA_EXPORT", export_dir)

    caminhos = bi_exporter.exportar_tudo()

    assert "geracoes" in caminhos
    csv_geracoes = Path(caminhos["geracoes"])
    assert csv_geracoes.exists()
    conteudo_csv = csv_geracoes.read_text(encoding="utf-8")
    assert "pacote_json" not in conteudo_csv


# ==============================================================================
# BLOCO 5: PIPELINE LLM E RESILIÊNCIA A FALHAS (RAG PIPELINE)
# ==============================================================================

def test_13_llm_pipeline_fallback_gemini_para_groq():
    """Cenário 13: Resiliência de IA — Gemini falha e Groq assume automaticamente."""
    from pipeline.llm_pipeline import gerar_de_contexto

    doc = DocumentoEntrada(documento_id="doc_ml", nome_arquivo="Machine_Learning.pdf")
    pedido = PedidoGeracao(
        documento=doc,
        perfil=Perfil.INICIANTE,
        formato=Formato.FLASHCARDS,
        nivel="basico",
        quantidade_itens=1,
    )
    trecho = TrechoRecuperado(
        chunk_id="doc_ml_p1_0",
        documento_id="doc_ml",
        texto="Machine Learning é um subcampo da IA.",
        paginas=[1],
        posicao=1,
    )
    contexto = ContextoRAG(pedido=pedido, trechos=[trecho])

    def mock_gemini(system, user):
        raise RuntimeError("503 UNAVAILABLE")

    json_valido = json.dumps({
        "formato": "Flashcards",
        "itens": [
            {
                "pergunta": "O que é ML?",
                "resposta": "Subcampo da inteligência artificial.",
                "classificacao": {"assunto": "IA", "subassunto": "ML", "nivel_dificuldade": "basico"},
                "fontes": [{"paginas": [1], "chunk_ids": ["doc_ml_p1_0"]}],
            }
        ],
    })

    def mock_groq(system, user):
        return json_valido, "openai/gpt-oss-120b"

    resultado = gerar_de_contexto(contexto, provedores=[mock_gemini, mock_groq])

    assert resultado.provedor == "mock_groq"
    assert len(resultado.erros_anteriores) == 1
    assert "mock_gemini" in resultado.erros_anteriores[0]
    assert resultado.pacote.metadados.modelo_llm == "openai/gpt-oss-120b"


def test_14_llm_pipeline_contexto_vazio_rejeitado():
    """Cenário 14: Contrato rejeita ContextoRAG sem trechos."""
    doc = DocumentoEntrada(documento_id="doc_ml", nome_arquivo="Machine_Learning.pdf")
    pedido = PedidoGeracao(
        documento=doc,
        perfil=Perfil.INICIANTE,
        formato=Formato.FLASHCARDS,
        nivel="basico",
    )
    with pytest.raises(ValidationError):
        ContextoRAG(pedido=pedido, trechos=[])


# ==============================================================================
# BLOCO 6: SEGURANÇA E CONFORMIDADE NO-COUNTRY
# ==============================================================================

def test_15_seguranca_scan_credenciais_em_codigo():
    """Cenário 15: Verificação de segurança — Garante que nenhuma API key foi commitada."""
    import re

    padrao_chave = re.compile(r"(AIza[0-9A-Za-z-_]{35}|gsk_[0-9A-Za-z]{40,})")
    arquivos_criticos = [
        _ROOT / "services" / "oci_secrets.py",
        _ROOT / "services" / "oci_storage.py",
        _ROOT / "services" / "bi_exporter.py",
        _ROOT / "rag" / ".env.example",
        _ROOT / "rag" / "main.py",
    ]
    for arq in arquivos_criticos:
        if arq.exists():
            matches = padrao_chave.findall(arq.read_text(encoding="utf-8"))
            assert len(matches) == 0, f"Possível vazamento de credencial em {arq.name}"


def test_16_no_country_requisitos_minimos_entregavel():
    """Cenário 16: Conformidade NoCountry — Valida campos mandatórios do PacoteFinal."""
    pacote_dict = {
        "metadados": {
            "documento_id": "doc_01",
            "perfil": "Iniciante",
            "formato": "Flashcards",
            "nivel": "basico",
            "tempo_estimado_estudo_minutos": 10,
            "conceitos_chave": ["IA", "ML"],
            "modelo_llm": "gemini-3.8-flash",
            "versao_prompt": "rag-llm-v1",
        },
        "conteudo_adaptado": {
            "formato": "Flashcards",
            "itens": [
                {
                    "pergunta": "O que é ML?",
                    "resposta": "Aprendizado de Máquina.",
                    "classificacao": {"assunto": "IA", "subassunto": "ML", "nivel_dificuldade": "basico"},
                    "fontes": [{"paginas": [1], "chunk_ids": ["doc_01_p1_0"]}],
                }
            ],
        },
        "avaliacao_qualidade": {
            "ancoragem_fonte_score": 0.95,
            "metodo_ancoragem": "estrutural",
            "observacoes": [],
        },
        "armazenamento_oci": {
            "status_upload": "sucesso",
            "bucket": "mentoria-tech-artifacts",
            "objeto_id": "resultado_20261112.json",
        },
    }
    pacote = PacoteFinal.model_validate(pacote_dict)
    assert pacote.metadados.perfil == Perfil.INICIANTE
    assert pacote.armazenamento_oci.bucket == "mentoria-tech-artifacts"
    assert pacote.armazenamento_oci.status_upload == "sucesso"


# ==============================================================================
# BLOCO 7: CONTRATO FASTAPI (rag/main.py) E PERSISTÊNCIA SQLITE
# ==============================================================================

@pytest.fixture
def api_client_isolado(tmp_path, monkeypatch):
    """Inicializa FastAPI TestClient com banco SQLite temporário isolado."""
    fastapi_testclient = pytest.importorskip("fastapi.testclient", reason="fastapi não instalado na .venv")
    import rag.database as rag_db
    import rag.main as rag_main

    db_temp = tmp_path / "qa_api.db"
    monkeypatch.setattr(rag_db, "DB_PATH", db_temp)
    monkeypatch.setattr(rag_main.db, "DB_PATH", db_temp)
    monkeypatch.setenv("GEMINI_API_KEY", "chave_fake_para_teste_contrato")
    rag_db.init_db()
    rag_db.migrate_respostas()

    with fastapi_testclient.TestClient(rag_main.app) as client:
        yield client, db_temp


def test_17_api_health_ok(api_client_isolado):
    """Cenário 17: GET /health retorna 200 {'status': 'ok'}."""
    client, _ = api_client_isolado
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_18_api_post_geracoes_rejeita_extensao_invalida(api_client_isolado):
    """Cenário 18: POST /geracoes rejeita arquivo .exe com HTTP 422."""
    client, _ = api_client_isolado
    resp = client.post(
        "/geracoes",
        files={"arquivo": ("malware.exe", b"binario", "application/octet-stream")},
        data={
            "perfil": "Iniciante",
            "nivel": "basico",
            "formato": "Quiz",
            "quantidade_itens": "1",
            "usuario_id": "u-test-1",
            "sessao_id": "s-test-1",
        },
    )
    assert resp.status_code == 422


def test_19_api_post_geracoes_quiz_sem_gabarito_e_persiste_sqlite(api_client_isolado):
    """Cenário 19: POST /geracoes com fixture .txt gera Quiz sem gabarito e persiste no SQLite."""
    client, db_temp = api_client_isolado
    from pipeline.llm_pipeline import ResultadoPipeline

    doc_in = DocumentoEntrada(documento_id="doc_fixture", nome_arquivo="aula.txt", tipo_arquivo="txt")
    doc_ext = DocumentoExtraido(
        documento=doc_in,
        paginas=[PaginaExtraida(documento_id="doc_fixture", pagina=1, texto="Aprendizado supervisionado usa rótulos.")],
    )
    trecho = TrechoRecuperado(
        chunk_id="doc_fixture_p1_0",
        documento_id="doc_fixture",
        texto="Aprendizado supervisionado usa rótulos.",
        paginas=[1],
        posicao=1,
    )
    quiz_conteudo = Quiz(
        formato="Quiz",
        questoes=[
            QuestaoQuiz(
                enunciado="O que usa o aprendizado supervisionado?",
                alternativas=["Dados rotulados", "Sem rótulos"],
                indice_resposta_correta=0,
                explicacao="Usa rótulos conhecidos.",
                classificacao=_classificacao_exemplo(),
                fontes=[_fonte_exemplo("doc_fixture_p1_0", [1])],
            )
        ],
    )
    pacote = PacoteFinal(
        metadados=Metadados(
            documento_id="doc_fixture",
            perfil=Perfil.INICIANTE,
            formato=Formato.QUIZ,
            nivel="basico",
            tempo_estimado_estudo_minutos=5,
            modelo_llm="gemini-3.8-flash",
            versao_prompt="rag-llm-v1",
        ),
        conteudo_adaptado=quiz_conteudo,
        avaliacao_qualidade=AvaliacaoQualidade(),
        armazenamento_oci=ArmazenamentoOCI(status_upload="pendente"),
    )
    res_pipe = ResultadoPipeline(pacote=pacote, provedor="mock", duracao_ms=120.5, erros_anteriores=[])

    mock_indice = MagicMock()
    mock_indice.__enter__.return_value = mock_indice
    mock_indice.recuperar.return_value = ContextoRAG(
        pedido=PedidoGeracao(documento=doc_in, perfil=Perfil.INICIANTE, formato=Formato.QUIZ, nivel="basico", quantidade_itens=1),
        trechos=[trecho],
    )

    adequacao_mock = SimpleNamespace(divergencia=False, mensagem=None)
    avaliacao_mock = SimpleNamespace(adequacao=adequacao_mock)

    with patch("backend.app.ingestao.processar_documento", return_value=doc_ext), \
         patch("pipeline.avaliacao_documento.avaliar_documento", return_value=(None, avaliacao_mock)), \
         patch("pipeline.avaliacao_documento.comparar_adequacao", return_value=adequacao_mock), \
         patch("pipeline.rag_retrieval.indice_documento", return_value=mock_indice), \
         patch("pipeline.llm_pipeline.gerar_de_contexto", return_value=res_pipe), \
         patch("rag.main.db.associar_telemetria_geracao"):
        resp = client.post(
            "/geracoes",
            files={"arquivo": ("aula.txt", b"Aprendizado supervisionado usa rotulos.", "text/plain")},
            data={
                "perfil": "Iniciante",
                "nivel": "basico",
                "formato": "Quiz",
                "quantidade_itens": "1",
                "usuario_id": "u-test-1",
                "sessao_id": "s-test-1",
            },
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["formato"] == "Quiz"
    assert "questoes" in body
    assert "indice_resposta_correta" not in body["questoes"][0]
    assert "explicacao" not in body["questoes"][0]

    con = sqlite3.connect(str(db_temp))
    row = con.execute("SELECT geracao_id, perfil, formato FROM geracoes WHERE geracao_id=?", (body["geracao_id"],)).fetchone()
    con.close()
    assert row is not None
    assert row[1] == "Iniciante"
    assert row[2] == "Quiz"
