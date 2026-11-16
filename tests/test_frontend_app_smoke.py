"""Testes smoke da interface Streamlit com AppTest e API simulada."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

_ROOT = Path(__file__).resolve().parent.parent
_APP = _ROOT / "app"
for _p in (str(_APP), str(_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)


class TestFrontendAppSmoke(unittest.TestCase):
    def test_telas_iniciam_limpas_sem_mocks_falsos(self):
        with (
            patch("api_client.verificar_saude", return_value=True),
            patch("api_client.listar_quizzes", return_value=[]),
        ):
            at = AppTest.from_file(str(_APP / "main.py"), default_timeout=30)
            at.run()
            self.assertFalse(at.exception, f"Exceção na Visão geral: {at.exception}")
            self.assertEqual(at.session_state["resultados"], [])
            self.assertEqual(at.session_state["documentos"], [])
            self.assertTrue(bool(at.session_state["usuario_id"]))
            self.assertTrue(bool(at.session_state["sessao_id"]))

            # Navega para Biblioteca, Estúdio e Meus conteúdos
            for btn_key in ("nav_Minha biblioteca", "nav_Estúdio de criação", "nav_Meus conteúdos"):
                at.sidebar.button(key=btn_key).click().run()
                self.assertFalse(at.exception, f"Exceção ao abrir {btn_key}: {at.exception}")

    def test_fluxo_geracao_e_quiz_sem_gabarito_com_tentativas_e_409(self):
        fake_questoes = [
            {
                "questao_indice": 0,
                "enunciado": "O que é uma VCN na OCI?",
                "alternativas": ["Rede virtual privada", "Banco de dados", "Container", "Storage frio"],
                "assunto": "Redes OCI",
            }
        ]
        fake_geracao = {
            "geracao_id": "quiz-uuid-0001",
            "formato": "Quiz",
            "perfil": "Tech Lead",
            "nivel_solicitado": "basico",
            "avaliacao_id": "av-001",
            "adequacao": {"divergencia": False, "mensagem": None},
            "duracao_ms": 950.0,
            "questoes": fake_questoes,
        }

        with (
            patch("api_client.verificar_saude", return_value=True),
            patch("api_client.listar_quizzes", return_value=[]),
            patch("api_client.gerar_conteudo", return_value=fake_geracao) as mock_gerar,
            patch("api_client.iniciar_rodada", return_value={"rodada_id": "rodada-1111", "geracao_id": "quiz-uuid-0001"}),
            patch("api_client.obter_historico", return_value=[
                {
                    "data_hora": "2026-11-15T23:00:00+00:00",
                    "rodada_id": "rodada-1111",
                    "questao_indice": 0,
                    "tentativa_numero": 1,
                    "alternativa_escolhida": 1,
                    "acertou": 0,
                    "assunto": "Redes OCI",
                }
            ]),
            patch(
                "oci_bridge.persistir_artefato",
                side_effect=lambda r: r.__setitem__(
                    "armazenamento_oci",
                    {"bucket": "mentoria-tech-artifacts", "objeto_id": "resultado_quiz-uuid-0001.json", "status_upload": "concluido"},
                ) or r["armazenamento_oci"],
            ),
        ):
            at = AppTest.from_file(str(_APP / "main.py"), default_timeout=30)
            at.run()

            # Carrega documento na Biblioteca via botão de exemplo ou texto manual
            at.sidebar.button(key="nav_Minha biblioteca").click().run()
            at.text_input[0].set_value("Guia VCN").run()
            at.text_area[0].set_value("A VCN é uma rede virtual privada na OCI.").run()
            at.button(label="+ Salvar Texto como .txt").click().run()
            self.assertEqual(len(at.session_state["documentos"]), 1)

            # Vai para o Estúdio de criação e verifica opção Tech Lead
            at.sidebar.button(key="nav_Estúdio de criação").click().run()
            self.assertIn("Líder Técnico / Arquiteto", at.selectbox[1].options)
            at.selectbox[1].select("Líder Técnico / Arquiteto").run()

            # Gera Quiz
            at.button(key="btn_gerar_conteudo").click().run()
            self.assertFalse(at.exception)
            mock_gerar.assert_called_once()
            self.assertEqual(mock_gerar.call_args.kwargs["perfil"], "Tech Lead")
            self.assertEqual(len(at.session_state["resultados"]), 1)

            # Verifica que o gabarito NÃO está presente no estado do Quiz inicialmente
            q_state = at.session_state["quiz"]["quiz-uuid-0001"]["questoes_estado"][0]
            self.assertIsNone(q_state["indice_correto"])
            self.assertIsNone(q_state["explicacao"])
            self.assertEqual(q_state["restantes"], 3)

            # Inicia rodada
            at.button(key="btn_rodada_studio_quiz-uuid-0001").click().run()
            self.assertEqual(at.session_state["quiz"]["quiz-uuid-0001"]["rodada_id"], "rodada-1111")

            # Simula 1ª tentativa errada (gabarito continua oculto, restantes = 2)
            with patch(
                "api_client.responder_questao",
                return_value={"acertou": False, "tentativa_numero": 1, "tentativas_restantes": 2, "questao_encerrada": False},
            ):
                at.radio(key="radio_studio_quiz-uuid-0001_rodada-1111_0").set_value(1)
                at.button(key="FormSubmitter:form_studio_quiz-uuid-0001_rodada-1111_0-Responder").click().run()

            q_state = at.session_state["quiz"]["quiz-uuid-0001"]["questoes_estado"][0]
            self.assertFalse(q_state["encerrada"])
            self.assertEqual(q_state["restantes"], 2)
            self.assertIsNone(q_state["indice_correto"])

            # Simula 2ª tentativa certa (libera gabarito e encerra)
            with patch(
                "api_client.responder_questao",
                return_value={
                    "acertou": True,
                    "tentativa_numero": 2,
                    "tentativas_restantes": 0,
                    "questao_encerrada": True,
                    "indice_resposta_correta": 0,
                    "explicacao": "VCN é a rede virtual privada da OCI.",
                },
            ):
                at.radio(key="radio_studio_quiz-uuid-0001_rodada-1111_0").set_value(0)
                at.button(key="FormSubmitter:form_studio_quiz-uuid-0001_rodada-1111_0-Responder").click().run()

            q_state = at.session_state["quiz"]["quiz-uuid-0001"]["questoes_estado"][0]
            self.assertTrue(q_state["encerrada"])
            self.assertEqual(q_state["indice_correto"], 0)
            self.assertEqual(q_state["explicacao"], "VCN é a rede virtual privada da OCI.")


if __name__ == "__main__":
    unittest.main()
