"""Testes unitários do cliente HTTP, ponte OCI e exportadores do frontend."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests

_ROOT = Path(__file__).resolve().parent.parent
_APP = _ROOT / "app"
for _p in (str(_APP), str(_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import api_client  # noqa: E402
import config  # noqa: E402
import identidade  # noqa: E402
import oci_bridge  # noqa: E402
import renderizadores  # noqa: E402


def _mock_response(status_code: int, json_data=None, text: str = "") -> MagicMock:
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    resp.ok = 200 <= status_code < 300
    resp.text = text or (json.dumps(json_data) if json_data is not None else "")
    if json_data is not None:
        resp.json.return_value = json_data
    else:
        resp.json.side_effect = ValueError("No JSON")
    return resp


class TestConfigAndIdentidade(unittest.TestCase):
    def test_perfis_inclui_tech_lead_e_nao_arquiteto(self):
        self.assertIn("Tech Lead", config.PERFIS.values())
        self.assertNotIn("Arquiteto", config.PERFIS.values())

    def test_quantidade_itens_demo_day(self):
        self.assertEqual(config.QTD_ITENS_MIN, 1)
        self.assertEqual(config.QTD_ITENS_MAX, 20)
        self.assertEqual(config.QTD_ITENS_PADRAO, 5)

    def test_validar_uuid(self):
        uid = "03dff47d-a7db-4c96-b770-45be626d2a1d"
        self.assertEqual(identidade.validar_uuid(uid), uid)
        self.assertIsNone(identidade.validar_uuid("teste_local"))
        self.assertIsNone(identidade.validar_uuid(""))
        self.assertIsNone(identidade.validar_uuid(None))


class TestApiClient(unittest.TestCase):
    def test_verificar_saude_ok_e_offline(self):
        sess = MagicMock(spec=requests.Session)
        sess.request.return_value = _mock_response(200, {"status": "ok"})
        self.assertTrue(api_client.verificar_saude(base_url="http://127.0.0.1:8000", session=sess))

        sess.request.side_effect = requests.exceptions.ConnectionError("refused")
        self.assertFalse(api_client.verificar_saude(base_url="http://127.0.0.1:8000", session=sess))

    def test_gerar_conteudo_multipart_sem_content_type_manual(self):
        sess = MagicMock(spec=requests.Session)
        sess.request.return_value = _mock_response(
            200,
            {
                "geracao_id": "g-123",
                "formato": "Quiz",
                "perfil": "Tech Lead",
                "nivel_solicitado": "intermediario",
                "avaliacao_id": "a-1",
                "adequacao": {"divergencia": False, "mensagem": None},
                "duracao_ms": 1200.5,
                "questoes": [],
            },
        )
        res = api_client.gerar_conteudo(
            arquivo_nome="manual.pdf",
            arquivo_bytes=b"%PDF-1.4",
            perfil="Tech Lead",
            nivel="intermediario",
            formato="Quiz",
            quantidade_itens=5,
            usuario_id="u-1",
            sessao_id="s-1",
            base_url="http://127.0.0.1:8000",
            session=sess,
        )
        self.assertEqual(res["geracao_id"], "g-123")
        _, kwargs = sess.request.call_args
        self.assertNotIn("headers", kwargs)
        self.assertEqual(kwargs["files"]["arquivo"], ("manual.pdf", b"%PDF-1.4", "application/pdf"))
        self.assertEqual(kwargs["data"]["usuario_id"], "u-1")
        self.assertEqual(kwargs["data"]["sessao_id"], "s-1")
        self.assertEqual(kwargs["data"]["perfil"], "Tech Lead")

    def test_tratamento_erros_http_string_e_lista(self):
        sess = MagicMock(spec=requests.Session)

        # 422 Pydantic com detail em lista
        sess.request.return_value = _mock_response(
            422,
            {"detail": [{"loc": ["body", "perfil"], "msg": "valor inválido"}]},
        )
        with self.assertRaises(api_client.ApiError) as ctx422:
            api_client.listar_quizzes("u-1", base_url="http://127.0.0.1:8000", session=sess)
        self.assertEqual(ctx422.exception.status, 422)
        self.assertIn("body.perfil: valor inválido", ctx422.exception.detalhe)

        # 409 Questão encerrada
        sess.request.return_value = _mock_response(409, {"detail": "Rodada encerrada."})
        with self.assertRaises(api_client.ApiError) as ctx409:
            api_client.responder_questao("g1", "u1", "s1", "r1", 0, 1, base_url="http://127.0.0.1:8000", session=sess)
        self.assertEqual(ctx409.exception.status, 409)
        self.assertIn("encerrada", ctx409.exception.mensagem_amigavel.lower())

        # 503 Chave Gemini ausente
        sess.request.return_value = _mock_response(503, {"detail": "RAG exige chave Gemini"})
        with self.assertRaises(api_client.ApiError) as ctx503:
            api_client.gerar_conteudo("a.txt", b"oi", "Iniciante", "basico", "Quiz", 5, "u1", "s1", session=sess)
        self.assertEqual(ctx503.exception.status, 503)
        self.assertIn("gemini", ctx503.exception.mensagem_amigavel.lower())

    def test_timeout_e_rede(self):
        sess = MagicMock(spec=requests.Session)
        sess.request.side_effect = requests.exceptions.Timeout("timed out")
        with self.assertRaises(api_client.ApiError) as ctx:
            api_client.consultar_quiz("g1", "u1", session=sess)
        self.assertIsNone(ctx.exception.status)
        self.assertIn("tempo limite", ctx.exception.mensagem_amigavel.lower())


class TestOciBridgeAndExport(unittest.TestCase):
    def test_pacote_artefato_sem_usuario_id_e_bucket_oficial(self):
        resultado = {
            "id": "gen-abc",
            "formato": "Quiz",
            "perfil": "Iniciante",
            "nivel": "basico",
            "documento_nome": "Machine_Learning.pdf",
            "quantidade_itens": 2,
            "criado_em": "15/11/2026 23:00",
            "duracao_ms": 1500.0,
            "avaliacao_id": "av-1",
            "adequacao": {"divergencia": False, "mensagem": None},
            "questoes": [
                {"questao_indice": 0, "enunciado": "P1?", "alternativas": ["A", "B"], "assunto": "ML"}
            ],
        }
        pacote = oci_bridge.montar_pacote_artefato(resultado)
        self.assertNotIn("usuario_id", json.dumps(pacote))

        with patch.object(oci_bridge, "_enviar_resultado_fn", return_value={
            "bucket": "mentoria-tech-artifacts",
            "objeto_id": "resultado_gen-abc.json",
            "status_upload": "concluido",
        }):
            with patch.object(oci_bridge, "OCI_DISPONIVEL", True):
                info = oci_bridge.persistir_artefato(resultado)
        self.assertEqual(info["bucket"], "mentoria-tech-artifacts")
        self.assertEqual(info["status_upload"], "concluido")

    def test_exportacao_quiz_nao_vaza_gabarito_antes_de_revelado(self):
        res_quiz = {
            "id": "gen-quiz-1",
            "formato": "Quiz",
            "perfil": "Iniciante",
            "nivel": "basico",
            "documento_nome": "doc.pdf",
            "questoes": [
                {"questao_indice": 0, "enunciado": "Qual o conceito?", "alternativas": ["Op0", "Op1"], "assunto": "ML"}
            ],
        }
        md_inicial = renderizadores._formatar_markdown(res_quiz, estado_quiz=None)
        self.assertNotIn("Gabarito revelado", md_inicial)

        estado_revelado = {
            "questoes_estado": {
                0: {"encerrada": True, "indice_correto": 1, "explicacao": "Op1 está correta."}
            }
        }
        md_pos = renderizadores._formatar_markdown(res_quiz, estado_quiz=estado_revelado)
        self.assertIn("Gabarito revelado:** B) Op1", md_pos)
        self.assertIn("Op1 está correta.", md_pos)

        csv_inicial = renderizadores._formatar_csv_anki(res_quiz, estado_quiz=None)
        self.assertNotIn("Op1 está correta", csv_inicial)


if __name__ == "__main__":
    unittest.main()
