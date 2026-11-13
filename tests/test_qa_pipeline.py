"""Suíte de Testes de QA e Integridade do Pipeline — MentorIA Tech (Equipe 26).

16 cenários de teste automatizados com pytest e unittest.mock.
NENHUMA chamada real de API ou OCI é executada aqui — execução 100% isolada e rápida.

Executar:
    pytest tests/test_qa_pipeline.py -v
"""

import json
import os
import sqlite3
import sys
from pathlib import Path
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
    Conteudo,
    ContextoRAG,
    Dificuldade,
    DocumentoEntrada,
    Flashcard,
    Flashcards,
    Fonte,
    Formato,
    Metadados,
    Nicho,
    PacoteFinal,
    PedidoGeracao,
    Perfil,
    QuestaoQuiz,
    Quiz,
    TrechoRecuperado,
    Tutorial,
)


# ==============================================================================
# BLOCO 1: SCHEMAS E CONTRATOS DE DADOS (PYDANTIC V2)
# ==============================================================================

def test_01_schema_documento_valido():
    """Cenário 1: Validação de documento de entrada com campos válidos."""
    doc = DocumentoEntrada(
        documento_id="doc_ml_01",
        nome_arquivo="Machine_Learning.pdf",
        tipo_arquivo="pdf"
    )
    assert doc.documento_id == "doc_ml_01"
    assert doc.tipo_arquivo == "pdf"


def test_02_schema_documento_invalido_rejeita_campos_extras():
    """Cenário 2: Validação estrita (extra='forbid') rejeita campos não declarados."""
    with pytest.raises(ValidationError):
        DocumentoEntrada(
            documento_id="doc_01",
            nome_arquivo="doc.pdf",
            campo_invalido_hacker="tentativa_injecao"
        )


def test_03_schema_pedido_geracao_perfis_e_formatos():
    """Cenário 3: Pedido de geração aceita os perfis e formatos da regra de negócio."""
    doc = DocumentoEntrada(documento_id="doc_01", nome_arquivo="Machine_Learning.pdf")
    pedido = PedidoGeracao(
        documento=doc,
        perfil=Perfil.INICIANTE,
        formato=Formato.FLASHCARDS,
        nicho=Nicho.GERAL,
        nivel="basico",
        quantidade_itens=5
    )
    assert pedido.perfil.value == "Iniciante"
    assert pedido.formato.value == "Flashcards"
    assert pedido.quantidade_itens == 5


def test_04_schema_conteudo_flashcards_valido():
    """Cenário 4: Validação de estrutura de Flashcards com fontes rastreáveis."""
    fonte = Fonte(chunk_id=1, paginas=[1, 2])
    card = Flashcard(
        frente="O que é Overfitting?",
        verso="Quando o modelo decora os dados de treino e erra em novos dados.",
        fontes=[fonte]
    )
    fc = Flashcards(formato="Flashcards", flashcards=[card])
    assert fc.formato == "Flashcards"
    assert len(fc.flashcards) == 1
    assert fc.flashcards[0].fontes[0].chunk_id == 1


def test_05_schema_quiz_rejeita_alternativas_duplicadas():
    """Cenário 5: QA de integridade — Quiz deve rejeitar alternativas duplicadas."""
    fonte = Fonte(chunk_id=2, paginas=[3])
    with pytest.raises(ValidationError) as exc:
        QuestaoQuiz(
            pergunta="Qual métrica avalia classificação?",
            alternativas=["Acurácia", "Acurácia", "F1-Score"],
            indice_resposta_correta=0,
            explicacao="Acurácia mede proporção de acertos.",
            classificacao=Classificacao(assunto="Avaliação", subassunto="Métricas", dificuldade=Dificuldade.BASICO),
            fontes=[fonte]
        )
    assert "Alternativas duplicadas" in str(exc.value)


def test_06_schema_pacote_final_consistencia_formato():
    """Cenário 6: QA de coerência — Metadados e ConteúdoAdaptado devem ter mesmo formato."""
    meta = Metadados(
        documento_id="doc_01",
        perfil=Perfil.INICIANTE,
        formato=Formato.FLASHCARDS,
        nicho=Nicho.GERAL,
        nivel="basico",
        tempo_estimado_estudo_minutos=10,
    )
    # Conteúdo diferente do formato declarado (Quiz em vez de Flashcards)
    fonte = Fonte(chunk_id=1, paginas=[1])
    quiz = Quiz(
        formato="Quiz",
        questoes=[
            QuestaoQuiz(
                pergunta="Pergunta?",
                alternativas=["A", "B"],
                indice_resposta_correta=0,
                explicacao="Exp",
                classificacao=Classificacao(assunto="A", subassunto=None, dificuldade=Dificuldade.BASICO),
                fontes=[fonte]
            )
        ]
    )
    with pytest.raises(ValidationError) as exc:
        PacoteFinal(
            metadados=meta,
            conteudo_adaptado=quiz,
            avaliacao_qualidade=AvaliacaoQualidade(),
            armazenamento_oci=ArmazenamentoOCI(status_upload="pendente")
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

def test_08_oci_secrets_pool_rotation():
    """Cenário 8: Pool de rotação alterna entre chaves disponíveis (Round-Robin)."""
    from services.oci_secrets import PoolChaves

    pool = PoolChaves(nome="TEST_POOL", chaves=["chave_alpha", "chave_beta"])
    k1 = pool.proxima()
    k2 = pool.proxima()
    k3 = pool.proxima()

    assert k1 == "chave_alpha"
    assert k2 == "chave_beta"
    assert k3 == "chave_alpha"  # Ciclo recomeça


def test_09_oci_secrets_fallback_chave_unica(monkeypatch):
    """Cenário 9: oci_secrets funciona tanto com chave única quanto com lista plural."""
    from services import oci_secrets

    # Simula apenas GEMINI_API_KEY no ambiente
    monkeypatch.setenv("GEMINI_API_KEY", "chave_unica_123")
    monkeypatch.delenv("GEMINI_API_KEYS", raising=False)
    oci_secrets._pool_gemini = None  # Reseta cache do módulo

    chave = oci_secrets.obter_chave_gemini()
    assert chave == "chave_unica_123"


# ==============================================================================
# BLOCO 3: STORAGE OCI E RESILIÊNCIA A FALHAS (SERVICES)
# ==============================================================================

def test_10_oci_storage_upload_sucesso_mock():
    """Cenário 10: Upload OCI concluído com sucesso retorna metadados conformes."""
    from services import oci_storage

    payload = {"teste": "dados_de_mentoria"}

    # Mock do cliente OCI
    mock_cliente = MagicMock()
    mock_cliente.put_object.return_value = MagicMock(status=200)

    with patch("oci.config.from_file", return_value={"namespace": "grclodnfw2hl"}), \
         patch("oci.object_storage.ObjectStorageClient", return_value=mock_cliente):
        
        resultado = oci_storage._tentar_upload_oci(payload, "resultado_demo.json")

    assert resultado["bucket"] == "mentoria-tech-artifacts"
    assert resultado["objeto_id"] == "resultado_demo.json"
    assert resultado["status_upload"] == "concluido"
    mock_cliente.put_object.assert_called_once()


def test_11_oci_storage_fallback_local_quando_sem_oci(tmp_path, monkeypatch):
    """Cenário 11: Se OCI indisponível, salva localmente em data/oci_fallback/."""
    from services import oci_storage

    # Redireciona a pasta de fallback para diretório temporário isolado
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

    # Cria banco SQLite de teste em memória/arquivo temporário
    db_file = tmp_path / "teste_novamente.db"
    con = sqlite3.connect(str(db_file))
    con.execute("""
        CREATE TABLE geracoes (
            id TEXT, documento_id TEXT, perfil TEXT, formato TEXT, 
            data_hora TEXT, pacote_json TEXT
        )
    """)
    con.execute("""
        INSERT INTO geracoes VALUES (
            'gen_1', 'doc_ml', 'Iniciante', 'Flashcards', 
            '2026-11-12T15:00:00Z', '{"conteudo": "bruto"}'
        )
    """)
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
    assert "pacote_json" not in conteudo_csv  # Coluna JSON bruto deve ser filtrada para o BI


# ==============================================================================
# BLOCO 5: PIPELINE LLM E RESILIÊNCIA A FALHAS (RAG PIPELINE)
# ==============================================================================

def test_13_llm_pipeline_fallback_gemini_para_groq():
    """Cenário 13: Resiliência de IA — Gemini falha com 503 e Groq assume automaticamente."""
    from pipeline.llm_pipeline import gerar_de_contexto

    # Prepara contexto de teste
    doc = DocumentoEntrada(documento_id="doc_ml", nome_arquivo="Machine_Learning.pdf")
    pedido = PedidoGeracao(
        documento=doc, perfil=Perfil.INICIANTE, formato=Formato.FLASHCARDS,
        nicho=Nicho.GERAL, nivel="basico", quantidade_itens=1
    )
    trecho = TrechoRecuperado(chunk_id=1, paginas=[1], texto="Machine Learning é um subcampo da IA.")
    contexto = ContextoRAG(pedido=pedido, trechos=[trecho])

    # Mock do Gemini: falha com erro 503 (sobrecarga)
    def mock_gemini(system, user):
        raise ServerError(503, "Demand spike: 503 UNAVAILABLE", {})

    # Mock do Groq: responde com JSON válido de Flashcards
    json_valido = json.dumps({
        "formato": "Flashcards",
        "flashcards": [
            {
                "frente": "O que é ML?",
                "verso": "Subcampo da inteligência artificial.",
                "fontes": [{"chunk_id": 1, "paginas": [1]}]
            }
        ]
    })
    def mock_groq(system, user):
        return json_valido, "openai/gpt-oss-120b"

    resultado = gerar_de_contexto(contexto, provedores=[mock_gemini, mock_groq])

    assert resultado.provedor == "mock_groq"
    assert len(resultado.erros_anteriores) == 1
    assert "mock_gemini" in resultado.erros_anteriores[0]
    assert resultado.pacote.metadados.modelo_llm == "openai/gpt-oss-120b"


def test_14_llm_pipeline_contexto_vazio_lanca_erro():
    """Cenário 14: Pipeline rejeita geração se não houver contexto RAG."""
    from pipeline.llm_pipeline import FalhaGeracao, gerar_de_contexto

    doc = DocumentoEntrada(documento_id="doc_ml", nome_arquivo="Machine_Learning.pdf")
    pedido = PedidoGeracao(
        documento=doc, perfil=Perfil.INICIANTE, formato=Formato.FLASHCARDS,
        nicho=Nicho.GERAL, nivel="basico"
    )
    contexto_vazio = ContextoRAG(pedido=pedido, trechos=[])

    with pytest.raises(FalhaGeracao):
        gerar_de_contexto(contexto_vazio)


# ==============================================================================
# BLOCO 6: SEGURANÇA E CONFORMIDADE NO-COUNTRY
# ==============================================================================

def test_15_seguranca_scan_credenciais_em_codigo():
    """Cenário 15: Verificação de segurança — Garante que nenhuma API key foi commitada."""
    import re
    padrao_chave = re.compile(r'(AIza[0-9A-Za-z-_]{35}|gsk_[0-9A-Za-z]{40,})')

    arquivos_criticos = [
        _ROOT / "services" / "oci_secrets.py",
        _ROOT / "services" / "oci_storage.py",
        _ROOT / "services" / "bi_exporter.py",
        _ROOT / "rag" / ".env.example",
    ]

    for arq in arquivos_criticos:
        if arq.exists():
            conteudo = arq.read_text(encoding="utf-8")
            matches = padrao_chave.findall(conteudo)
            assert len(matches) == 0, f"Possível vazamento de credencial em {arq.name}: {matches}"


def test_16_no_country_requisitos_minimos_entregavel():
    """Cenário 16: Conformidade NoCountry — Valida campos mandatórios do entregável."""
    pacote_dict = {
        "metadados": {
            "documento_id": "doc_01",
            "perfil": "Iniciante",
            "formato": "Flashcards",
            "nicho": "Geral",
            "nivel": "basico",
            "tempo_estimado_estudo_minutos": 10,
            "conceitos_chave": ["IA", "ML"],
            "modelo_llm": "gemini-3.8-flash",
            "versao_prompt": "rag-llm-v1"
        },
        "conteudo_adaptado": {
            "formato": "Flashcards",
            "flashcards": [
                {
                    "frente": "O que é ML?",
                    "verso": "Aprendizado de Máquina.",
                    "fontes": [{"chunk_id": 1, "paginas": [1]}]
                }
            ]
        },
        "avaliacao_qualidade": {
            "ancoragem_fonte_score": 0.95,
            "metodo_ancoragem": "estrutural",
            "observacoes": []
        },
        "armazenamento_oci": {
            "status_upload": "sucesso",
            "bucket": "mentoria-tech-artifacts",
            "objeto_id": "resultado_20261112.json"
        }
    }
    pacote = PacoteFinal.model_validate(pacote_dict)
    assert pacote.metadados.perfil == Perfil.INICIANTE
    assert pacote.armazenamento_oci.bucket == "mentoria-tech-artifacts"
    assert pacote.armazenamento_oci.status_upload == "sucesso"
