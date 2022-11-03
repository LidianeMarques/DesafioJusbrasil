from unicodedata import normalize

import requests
from fastapi.encoders import jsonable_encoder
from lxml import etree

from model import ParteProcesso, Adovogado, DadosColetados, MovimentacoesProcesso
from utils import formatar_texto


class ScrapPrimeiraInstancia():
    url_base = 'https://www2.tjal.jus.br'
    parametros = "conversationId=&cbPesquisa=NUMPROC&numeroDigitoAnoUnificado={num_dig_ano}&foroNumeroUnificado={foro}&dadosConsulta.valorConsultaNuUnificado={num_processo}&dadosConsulta.valorConsultaNuUnificado=UNIFICADO&dadosConsulta.valorConsulta=&dadosConsulta.tipoNuProcesso=UNIFICADO"

    # https://esaj.tjce.jus.br/cpopg/search.do?conversationId=&cbPesquisa=NUMPROC&numeroDigitoAnoUnificado=0070337-91.2008&foroNumeroUnificado=0001&dadosConsulta.valorConsultaNuUnificado=0070337-91.2008.8.06.0001&dadosConsulta.valorConsultaNuUnificado=UNIFICADO&dadosConsulta.valorConsulta=&dadosConsulta.tipoNuProcesso=UNIFICADO

    def start_requests(self, numero_processo):
        print('====> Start Request <====')
        # O numero_processo o usuário que vai ter que dar
        codigo_num_processo = numero_processo
        split_codigo = codigo_num_processo.split(".")
        num_dig_ano = ".".join(split_codigo[:2])  # "0710802-55.2018"
        foro = split_codigo[-1]  # "0001"
        num_processo = codigo_num_processo  # '0070337-91.2008.8.06.0001'
        param = self.parametros.format(num_dig_ano=num_dig_ano, foro=foro,
                                       num_processo=num_processo, dont_filter=True)
        response = requests.get(f"{self.url_base}/cpopg/search.do?{param}")

        if response.status_code == 200:
            return self.parse(response, numero_processo=numero_processo)

    def parse(self, response, **kwargs):
        print('====> Start Parsing <====')
        numero_processo = kwargs["numero_processo"]
        # Começando o scraping
        selector = etree.HTML(response.text)

        if selector.xpath('//*[@id="mensagemRetorno"]//text()'):
            return {'mensagem': 'Não existe processo!'}

        instancia_processo = selector.xpath('//nav[@class="header__navbar"]/h1/text()')[0].replace(" | ", "")
        classe = selector.xpath('//span[@id="classeProcesso"]//text()')[0]
        area = selector.xpath('//div[@id="areaProcesso"]/span//text()')[0]
        assunto = selector.xpath('//span[@id="assuntoProcesso"]//text()')[0]
        data_distribuicao = str(
            selector.xpath('//div[@id="dataHoraDistribuicaoProcesso"]//text()')[0]).split('às')[0]
        juiz = (selector.xpath('//span[@id="juizProcesso"]//text()')[0] if
                selector.xpath('//span[@id="juizProcesso"]//text()') else '')
        valor_acao = (selector.xpath('//div[@id="valorAcaoProcesso"]//text()')[0] if
                      selector.xpath('//div[@id="valorAcaoProcesso"]//text()') else '')
        valor_acao = valor_acao.replace('         ', ' ')

        # Parte do processo, são: Autor, Autora, Ré e Réu...
        lista_partes_processo = []
        for item in selector.xpath('//table[2]//tr'):
            nome_parte = formatar_texto([item.xpath('./td[2]//text()')[0]])
            tipo_parte = formatar_texto([item.xpath('./td[1]/span/text()')[0].upper()])
            # Tirar a acentuação das partes do processo
            tipo_parte = normalize("NFD", tipo_parte).encode("ascii", "ignore").decode("utf-8")

            lista_advogados = []
            advogados = formatar_texto(item.xpath('./td[2]//text()')[2:])
            if advogados.strip() != '' and advogados.strip().__contains__('\n'):
                advogados = advogados.split("\n")
                for index in range(0, len(advogados), 2):
                    tipo_advogado = advogados[index].upper()
                    nome_advogado = advogados[index + 1]
                    lista_advogados.append(Adovogado(tipo=tipo_advogado, nome=nome_advogado))

            lista_partes_processo.append(jsonable_encoder(ParteProcesso(tipo=tipo_parte,
                                                                        nome=nome_parte,
                                                                        advogados=lista_advogados)))

        # Movimentações do processo: data e movimento
        lista_movimentacoes = []
        itens_movimentacoes = selector.xpath('//*[@id="tabelaTodasMovimentacoes"]/tr')
        for movimentacao in itens_movimentacoes:
            data_movimentacao = movimentacao.xpath('./td[1]/text()')[0].strip()
            movimento = formatar_texto(movimentacao.xpath('./td[3]//text()'))
            lista_movimentacoes.append(jsonable_encoder(
                MovimentacoesProcesso(data_movimentacao=data_movimentacao, movimento=movimento)
            ))

        # Add os Dados coletados no model
        dados_coletados = []
        dados_coletados.append(DadosColetados(instancia_processo=instancia_processo,
                                              num_processo=numero_processo,
                                              classe=classe,
                                              area=area,
                                              assunto=assunto,
                                              data_distribuicao=data_distribuicao,
                                              autoridade_julgadora=juiz,
                                              valor_acao=valor_acao,
                                              partes_processo=lista_partes_processo,
                                              movimentacoes_processo=lista_movimentacoes))

        return dados_coletados
