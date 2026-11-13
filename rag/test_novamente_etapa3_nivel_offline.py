"""Testes offline da entrega do Quiz: sem chamadas reais às APIs."""
import json
import unittest
from unittest.mock import patch
from pipeline import llm_pipeline as llm
from pipeline.schemas import Formato
from test_novamente_offline import contexto, conteudo_exemplo

class TesteEntregaQuiz(unittest.TestCase):
    def _gerador(self, chamadas):
        def gerar(system, user, **kwargs):
            chamadas.append('geracao')
            exemplo = conteudo_exemplo(Formato.QUIZ)
            # Fixture coerente com os cenários que solicitam nível avançado.
            # Não modifica a validação do pipeline nem os testes anteriores.
            exemplo["questoes"][0]["classificacao"]["nivel_dificuldade"] = "avancado"
            return json.dumps(exemplo), 'mock'
        return gerar

    def test_quiz_avancado_auditado_e_entregue(self):
        ctx = contexto(Formato.QUIZ, nivel='avancado', auditoria=True)
        chamadas=[]
        def auditor(system, user, **kwargs):
            chamadas.append('auditoria')
            self.assertIn('avancado', user)
            return json.dumps({'itens':[{'indice':0,'factual':True,'resposta_correta':True,
                'distratores':True,'nivel_real':'avancado','motivo':'OK'}]}), 'mock'
        res = llm.gerar_de_contexto(ctx, provedores=[self._gerador(chamadas)], avaliador=auditor)
        self.assertEqual(chamadas,['geracao','auditoria'])
        self.assertEqual(res.pacote.metadados.nivel_efetivo,'avancado')

    def test_reprovacao_entrega_versao_original_sem_terceira_chamada(self):
        ctx=contexto(Formato.QUIZ,nivel='avancado',auditoria=True)
        chamadas=[]
        def auditor(*args,**kwargs):
            chamadas.append('auditoria')
            return json.dumps({'itens':[{'indice':0,'factual':False,'resposta_correta':True,
                'distratores':True,'nivel_real':'basico','motivo':'sem suporte'}]}),'mock'
        res=llm.gerar_de_contexto(ctx,provedores=[self._gerador(chamadas)],avaliador=auditor)
        self.assertEqual(chamadas,['geracao','auditoria'])
        self.assertEqual(res.pacote.metadados.nivel_efetivo,'avancado')
        self.assertIn('não aprovada', ' '.join(res.pacote.avaliacao_qualidade.observacoes))

    def test_auditoria_indisponivel_nao_bloqueia_entrega(self):
        ctx=contexto(Formato.QUIZ,nivel='avancado',auditoria=True)
        chamadas=[]
        def auditor(*args,**kwargs):
            chamadas.append('auditoria')
            raise llm.FalhaGeracao('HTTP 429 simulado')
        res=llm.gerar_de_contexto(ctx,provedores=[self._gerador(chamadas)],avaliador=auditor)
        self.assertEqual(chamadas,['geracao','auditoria'])
        self.assertIn('não aprovada', ' '.join(res.pacote.avaliacao_qualidade.observacoes))

    def test_sem_orcamento_auditoria_entrega_quiz(self):
        ctx=contexto(Formato.QUIZ,nivel='avancado',auditoria=True)
        ctx.pedido.politica_tokens.max_avaliacoes_llm=0
        chamadas=[]
        res=llm.gerar_de_contexto(ctx,provedores=[self._gerador(chamadas)])
        self.assertEqual(chamadas,['geracao'])
        self.assertIn('omitida', ' '.join(res.pacote.avaliacao_qualidade.observacoes))

    def test_nivel_estimado_inferior_nao_rebaixa_silenciosamente(self):
        ctx=contexto(Formato.QUIZ,nivel='avancado',auditoria=True)
        def auditor(*args,**kwargs):
            return json.dumps({'itens':[{'indice':0,'factual':True,'resposta_correta':True,
                'distratores':True,'nivel_real':'basico','motivo':'recordação'}]}),'mock'
        res=llm.gerar_de_contexto(ctx,provedores=[self._gerador([])],avaliador=auditor)
        self.assertEqual(res.pacote.metadados.nivel_efetivo,'basico')
        self.assertEqual(res.pacote.metadados.nivel_solicitado,'avancado')
        self.assertIn('auditoria pedagógica estimou dificuldade inferior', res.pacote.metadados.motivo_adaptacao)
        self.assertIn('inferior', ' '.join(res.pacote.avaliacao_qualidade.observacoes))

if __name__=='__main__': unittest.main()
