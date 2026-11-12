"""NovaMente: contratos Pydantic v2, um documento por execução, sem chamadas de API."""
from enum import Enum
from typing import Annotated, Literal, Union
from pydantic import BaseModel, ConfigDict, Field, model_validator

class Estrito(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class Perfil(str, Enum):
    INICIANTE='Iniciante'; JR_PLENO='Jr/Pleno'; ARQUITETO='Tech Lead'; GESTOR='Gestor'
class Formato(str, Enum):
    TUTORIAL='Tutorial'; FLASHCARDS='Flashcards'; QUIZ='Quiz'; TLDR='TL;DR'; ROTEIRO='Roteiro'; RESUMO='Resumo'
class Dificuldade(str, Enum):
    BASICO='basico'; INTERMEDIARIO='intermediario'; AVANCADO='avancado'

class DocumentoEntrada(Estrito):
    documento_id: str = Field(min_length=1)
    nome_arquivo: str = Field(min_length=1)
    tipo_arquivo: Literal['pdf','md','txt'] = 'pdf'

class PoliticaTokens(Estrito):
    permitir_avaliacao_llm: bool = False
    max_tokens_avaliacao_por_resposta: int = Field(default=250, ge=1, le=4096)
    max_tokens_avaliacao_total: int = Field(default=0, ge=0)
    max_avaliacoes_llm: int = Field(default=0, ge=0)

class PedidoGeracao(Estrito):
    documento: DocumentoEntrada
    perfil: Perfil
    formato: Formato
    nivel: str = Field(min_length=1)
    quantidade_itens: int | None = Field(default=None, ge=1, le=100)
    instrucoes_adicionais: str | None = None
    politica_tokens: PoliticaTokens = Field(default_factory=PoliticaTokens)

class PaginaExtraida(Estrito):
    documento_id: str = Field(min_length=1)
    pagina: int = Field(ge=1)
    texto: str = Field(min_length=1)
class DocumentoExtraido(Estrito):
    documento: DocumentoEntrada
    paginas: list[PaginaExtraida] = Field(min_length=1)
    @model_validator(mode='after')
    def validar_paginas(self):
        if any(p.documento_id != self.documento.documento_id for p in self.paginas):
            raise ValueError('Página de outro documento')
        if len({p.pagina for p in self.paginas}) != len(self.paginas):
            raise ValueError('Páginas repetidas')
        return self

class TrechoRecuperado(Estrito):
    chunk_id: str = Field(min_length=1)
    documento_id: str = Field(min_length=1)
    texto: str = Field(min_length=1)
    paginas: list[int] = Field(min_length=1)
    posicao: int = Field(ge=1)
    score_recuperacao: float | None = None
    score_reranker: float | None = None
    @model_validator(mode='after')
    def validar_paginas(self):
        if any(p < 1 for p in self.paginas):
            raise ValueError('Página inválida')
        return self
class ContextoRAG(Estrito):
    pedido: PedidoGeracao
    trechos: list[TrechoRecuperado] = Field(min_length=1)
    @model_validator(mode='after')
    def validar_documento(self):
        if any(t.documento_id != self.pedido.documento.documento_id for t in self.trechos):
            raise ValueError('Chunk de outro documento')
        return self

class Fonte(Estrito):
    paginas: list[int] = Field(min_length=1)
    chunk_ids: list[str] = Field(default_factory=list)
    @model_validator(mode='after')
    def validar_paginas(self):
        if any(p < 1 for p in self.paginas):
            raise ValueError('Página inválida')
        return self
class Classificacao(Estrito):
    assunto: str = Field(min_length=1)
    subassunto: str | None = None
    nivel_dificuldade: Dificuldade

class PassoTutorial(Estrito):
    titulo: str = Field(min_length=1)
    explicacao: str = Field(min_length=1)
    fontes: list[Fonte] = Field(min_length=1)
class Tutorial(Estrito):
    formato: Literal['Tutorial'] = 'Tutorial'
    titulo: str = Field(min_length=1)
    passos: list[PassoTutorial] = Field(min_length=1)

class Flashcard(Estrito):
    pergunta: str = Field(min_length=1)
    resposta: str = Field(min_length=1)
    classificacao: Classificacao
    fontes: list[Fonte] = Field(min_length=1)
    # A resposta é exibida pelo app; não há avaliação automática obrigatória.
class Flashcards(Estrito):
    formato: Literal['Flashcards'] = 'Flashcards'
    itens: list[Flashcard] = Field(min_length=1)

class QuestaoQuiz(Estrito):
    enunciado: str = Field(min_length=1)
    alternativas: list[str] = Field(min_length=2, max_length=6)
    indice_resposta_correta: int = Field(ge=0)
    explicacao: str = Field(min_length=1)
    classificacao: Classificacao
    fontes: list[Fonte] = Field(min_length=1)
    @model_validator(mode='after')
    def validar_alternativas(self):
        if self.indice_resposta_correta >= len(self.alternativas):
            raise ValueError('Índice da resposta fora do intervalo')
        if any(not x.strip() for x in self.alternativas):
            raise ValueError('Alternativa vazia')
        if len({x.strip().casefold() for x in self.alternativas}) != len(self.alternativas):
            raise ValueError('Alternativas duplicadas')
        return self
class Quiz(Estrito):
    formato: Literal['Quiz'] = 'Quiz'
    questoes: list[QuestaoQuiz] = Field(min_length=1)

class ResumoTLDR(Estrito):
    formato: Literal['TL;DR'] = 'TL;DR'
    resumo: str = Field(min_length=1)
    pontos_chave: list[str] = Field(min_length=1)
    fontes: list[Fonte] = Field(min_length=1)
class SecaoResumo(Estrito):
    titulo: str = Field(min_length=1)
    texto: str = Field(min_length=1)
    fontes: list[Fonte] = Field(min_length=1)
class Resumo(Estrito):
    # Extensão opcional aos cinco formatos do Trello: resumo mais detalhado que TL;DR.
    formato: Literal['Resumo'] = 'Resumo'
    titulo: str = Field(min_length=1)
    secoes: list[SecaoResumo] = Field(min_length=1)
class EtapaRoteiro(Estrito):
    atividade: str = Field(min_length=1)
    duracao_minutos: int = Field(ge=1)
    fontes: list[Fonte] = Field(min_length=1)
class Roteiro(Estrito):
    formato: Literal['Roteiro'] = 'Roteiro'
    etapas: list[EtapaRoteiro] = Field(min_length=1)

Conteudo = Annotated[Union[Tutorial,Flashcards,Quiz,ResumoTLDR,Roteiro,Resumo], Field(discriminator='formato')]

class Metadados(Estrito):
    documento_id: str = Field(min_length=1)
    perfil: Perfil
    formato: Formato
    nivel: str = Field(min_length=1)
    tempo_estimado_estudo_minutos: int = Field(ge=0)
    conceitos_chave: list[str] = Field(default_factory=list)
    modelo_llm: str | None = None
    versao_prompt: str | None = None
    # Campos opcionais para compatibilidade com registros antigos.
    nivel_solicitado: str | None = None
    nivel_efetivo: str | None = None
    perfil_solicitado: Perfil | None = None
    perfil_efetivo: Perfil | None = None
    motivo_adaptacao: str | None = None
class AvaliacaoQualidade(Estrito):
    ancoragem_fonte_score: float | None = Field(default=None, ge=0, le=1)
    metodo_ancoragem: str | None = None
    observacoes: list[str] = Field(default_factory=list)
class ArmazenamentoOCI(Estrito):
    status_upload: Literal['pendente','sucesso','erro'] = 'pendente'
    bucket: str | None = None
    objeto_id: str | None = None
    @model_validator(mode='after')
    def validar_upload(self):
        if self.status_upload == 'sucesso' and (not self.bucket or not self.objeto_id):
            raise ValueError('Upload concluído requer bucket e objeto_id')
        return self
class PacoteFinal(Estrito):
    metadados: Metadados
    conteudo_adaptado: Conteudo
    avaliacao_qualidade: AvaliacaoQualidade
    armazenamento_oci: ArmazenamentoOCI
    @model_validator(mode='after')
    def validar_formato(self):
        if self.metadados.formato.value != self.conteudo_adaptado.formato:
            raise ValueError('Formato dos metadados difere do conteúdo')
        return self

# Interações do estudante são registros separados do JSON final de geração.
class RespostaQuiz(Estrito):
    geracao_id: str = Field(min_length=1)
    questao_indice: int = Field(ge=0)
    alternativa_escolhida: int = Field(ge=0)
class ResultadoQuiz(Estrito):
    acertou: bool
    indice_resposta_correta: int = Field(ge=0)
    explicacao: str
    assunto: str
    subassunto: str | None = None

class PedidoAvaliacaoAberta(Estrito):
    pergunta: str = Field(min_length=1)
    resposta_referencia: str = Field(min_length=1)
    resposta_usuario: str = Field(min_length=1)
    fontes: list[Fonte] = Field(min_length=1)
class ResultadoAvaliacaoAberta(Estrito):
    avaliador: Literal['llm'] = 'llm'
    correto: bool | None = None
    feedback_curto: str = Field(min_length=1)
    # Não registrar raciocínio interno da LLM.
class TelemetriaGeracao(Estrito):
    geracao_id: str = Field(min_length=1)
    modelo_llm: str = Field(min_length=1)
    tokens_entrada: int | None = Field(default=None, ge=0)
    tokens_saida: int | None = Field(default=None, ge=0)
    latencia_segundos: float | None = Field(default=None, ge=0)
    quantidade_chunks: int = Field(ge=0)
    avaliacoes_llm_executadas: int = Field(default=0, ge=0)
