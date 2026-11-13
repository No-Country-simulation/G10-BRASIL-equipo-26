"""Testes locais do NovaMente: nenhuma chamada a Gemini/Groq ou SQLite.

Coloque este arquivo na pasta rag e execute:
    python -m unittest -v test_novamente_offline.py
"""
import json
import unittest
from unittest.mock import patch

from pipeline import llm_pipeline as llm
from pipeline.schemas import (
    ContextoRAG, DocumentoEntrada, Formato, PedidoGeracao,
    Perfil, PoliticaTokens, TrechoRecuperado, PacoteFinal,
)

FONTE = {"paginas": [1], "chunk_ids": ["c1"]}
CLASSIFICACAO = {"assunto": "Conceito", "nivel_dificuldade": "basico"}


def contexto(formato, *, nivel="basico", auditoria=False):
    documento = DocumentoEntrada(documento_id="doc1", nome_arquivo="exemplo.pdf")
    return ContextoRAG(
        pedido=PedidoGeracao(
            documento=documento, perfil=Perfil.INICIANTE,
            formato=formato, nivel=nivel, quantidade_itens=1,
            politica_tokens=PoliticaTokens(
                permitir_avaliacao_llm=auditoria,
                max_tokens_avaliacao_por_resposta=1000 if auditoria else 250,
                max_tokens_avaliacao_total=1000 if auditoria else 0,
                max_avaliacoes_llm=1 if auditoria else 0,
            ),
        ),
        trechos=[TrechoRecuperado(
            chunk_id="c1", documento_id="doc1", texto="Um conceito verificável.",
            paginas=[1], posicao=1,
        )],
    )


def conteudo_exemplo(formato):
    f = formato.value
    if formato == Formato.TUTORIAL:
        return {"formato": f, "titulo": "Guia", "passos": [
            {"titulo": "Etapa", "explicacao": "Texto", "fontes": [FONTE]}]}
    if formato == Formato.FLASHCARDS:
        return {"formato": f, "itens": [
            {"pergunta": "O quê?", "resposta": "Conceito", "classificacao": CLASSIFICACAO, "fontes": [FONTE]}]}
    if formato == Formato.QUIZ:
        return {"formato": f, "questoes": [
            {"enunciado": "Qual?", "alternativas": ["A", "B", "C", "D"],
             "indice_resposta_correta": 0, "explicacao": "A é correta.",
             "classificacao": CLASSIFICACAO, "fontes": [FONTE]}]}
    if formato == Formato.TLDR:
        return {"formato": f, "resumo": "Resumo", "pontos_chave": ["Conceito"], "fontes": [FONTE]}
    if formato == Formato.ROTEIRO:
        return {"formato": f, "etapas": [
            {"atividade": "Estudar", "duracao_minutos": 10, "fontes": [FONTE]}]}
    if formato == Formato.RESUMO:
        return {"formato": f, "titulo": "Resumo", "secoes": [
            {"titulo": "Seção", "texto": "Conceito", "fontes": [FONTE]}]}
    raise AssertionError(formato)


class TestesOffline(unittest.TestCase):
    def test_seis_formatos_com_provedor_simulado(self):
        for formato in Formato:
            with self.subTest(formato=formato.value):
                ctx = contexto(formato)
                def provedor(system, user, max_output_tokens=None):
                    self.assertIn("TRECHOS DO DOCUMENTO", user)
                    return json.dumps(conteudo_exemplo(formato)), "mock-local"
                resultado = llm.gerar_de_contexto(ctx, provedores=[provedor])
                pacote = PacoteFinal.model_validate(resultado.pacote.model_dump())
                self.assertEqual(pacote.conteudo_adaptado.formato, formato.value)
                self.assertEqual(pacote.metadados.modelo_llm, "mock-local")

    def test_fallback_apos_erro_tecnico(self):
        ctx = contexto(Formato.TUTORIAL)
        chamadas = []
        def indisponivel(*args, **kwargs):
            chamadas.append("principal")
            raise llm.FalhaGeracao("429 simulado")
        def reserva(*args, **kwargs):
            chamadas.append("reserva")
            return json.dumps(conteudo_exemplo(Formato.TUTORIAL)), "mock-reserva"
        resultado = llm.gerar_de_contexto(ctx, provedores=[indisponivel, reserva])
        self.assertEqual(chamadas, ["principal", "reserva"])
        self.assertEqual(resultado.pacote.metadados.modelo_llm, "mock-reserva")

    def test_falha_quando_todos_provedores_indisponiveis(self):
        def indisponivel(*args, **kwargs):
            raise llm.FalhaGeracao("429 simulado")
        with self.assertRaisesRegex(llm.FalhaGeracao, "Falha técnica"):
            llm.gerar_de_contexto(contexto(Formato.RESUMO), provedores=[indisponivel])

    def test_rejeita_chunk_inexistente(self):
        data = conteudo_exemplo(Formato.TUTORIAL)
        data["passos"][0]["fontes"] = [{"paginas": [1], "chunk_ids": ["inventado"]}]
        with self.assertRaisesRegex(llm.FalhaGeracao, "chunk inexistente"):
            llm._validar_conteudo(json.dumps(data), contexto(Formato.TUTORIAL))

    def test_rejeita_pagina_inexistente(self):
        data = conteudo_exemplo(Formato.TUTORIAL)
        data["passos"][0]["fontes"] = [{"paginas": [99], "chunk_ids": ["c1"]}]
        with self.assertRaisesRegex(llm.FalhaGeracao, "página fora"):
            llm._validar_conteudo(json.dumps(data), contexto(Formato.TUTORIAL))

    def test_rejeita_quiz_com_alternativas_duplicadas(self):
        data = conteudo_exemplo(Formato.QUIZ)
        data["questoes"][0]["alternativas"] = ["A", "A", "C", "D"]
        with self.assertRaisesRegex(llm.FalhaGeracao, "Pydantic"):
            llm._validar_conteudo(json.dumps(data), contexto(Formato.QUIZ))

    def test_rejeita_json_invalido(self):
        with self.assertRaisesRegex(llm.FalhaGeracao, "JSON válido"):
            llm._validar_conteudo("{invalido", contexto(Formato.RESUMO))

    def test_quiz_com_auditoria_simulada(self):
        ctx = contexto(Formato.QUIZ, auditoria=True)
        def gerador(*args, **kwargs):
            return json.dumps(conteudo_exemplo(Formato.QUIZ)), "mock-gerador"
        def auditor(*args, **kwargs):
            return json.dumps({"itens": [{"indice": 0, "factual": True,
                "resposta_correta": True, "distratores": True,
                "nivel_real": "basico", "motivo": "OK"}]}), "mock-auditor"
        resultado = llm.gerar_de_contexto(ctx, provedores=[gerador], avaliador=auditor)
        self.assertEqual(resultado.pacote.conteudo_adaptado.formato, "Quiz")


if __name__ == "__main__":
    unittest.main()
