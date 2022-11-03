from typing import List

from pydantic import BaseModel


# def __init__(self):
#     self.num_processo = "numero do 33444"
#     self.classe = "classe"
#     self.area = "area"
#     self.assunto = ""
#     self.data_distribuicao = ""
#     self.juiz = ""
#     self.valor_acao = ""
# self.partes_processo = []
# self.movimentacoes_processo = []


class Adovogado(BaseModel):
    tipo: str
    nome: str


class ParteProcesso(BaseModel):
    tipo: str
    nome: str
    advogados: List[Adovogado] = []


class MovimentacoesProcesso(BaseModel):
    data_movimentacao: str
    movimento: str


class DadosColetados(BaseModel):
    instancia_processo:str
    num_processo: str
    classe: str
    area: str
    assunto: str
    data_distribuicao: str = None
    autoridade_julgadora: str
    valor_acao: str
    partes_processo: List[ParteProcesso]
    movimentacoes_processo: List[MovimentacoesProcesso]
