from time import sleep
from unicodedata import normalize

import requests
from fastapi.encoders import jsonable_encoder
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By

from model import ParteProcesso, Adovogado, DadosColetados, MovimentacoesProcesso
from utils import formatar_texto


class ScrapSegundaInstancia():
    url_base = 'https://www2.tjal.jus.br'

    def start_requests(self, numero_processo):
        print('====> Start Request <====')
        # O numero_processo o usuário que vai ter que dar '0710802-55.2018.8.02.0001'
        codigo_num_processo = numero_processo
        split_codigo = codigo_num_processo.split(".")
        num_dig_ano = ".".join(split_codigo[:2])  # "0710802-55.2018"
        foro = split_codigo[-1]  # "0001"

        # O chromeDriver está na pasta raiz do projeto
        driver = webdriver.Chrome()
        driver.get(f'{self.url_base}/cposg5/open.do')
        sleep(0.2)
        caixa_numero = driver.find_element(By.ID, 'numeroDigitoAnoUnificado')
        caixa_numero.send_keys(num_dig_ano)
        caixa_numero = driver.find_element(By.ID, 'foroNumeroUnificado')
        caixa_numero.send_keys(foro)
        button = driver.find_element(By.ID, "pbConsultar")
        button.click()
        existe = False
        # Tem que ver como para o processo aqui se não tiver na segunda instancia
        try:
            checked = driver.find_element(By.ID, "processoSelecionado")
            checked.click()
            existe = True
        except Exception:
            driver.close()
            existe = False
        if existe:
            processo_selecionado = driver.find_element(By.ID, "processoSelecionado")
            codigo_processo_selecionado = processo_selecionado.get_attribute("value")
            driver.close()
            url = f"{self.url_base}/cposg5/show.do?processo.codigo={codigo_processo_selecionado}"
            response = requests.get(url)

            if response.status_code == 200:
                return self.parse(response, numero_processo=numero_processo)
        else:
            return {'mensagem': 'Não existe processo!'}

    def parse(self, response, **kwargs):
        print('====> Start Parsing <====')
        numero_processo = kwargs["numero_processo"]
        # Começando o scraping
        selector = etree.HTML(response.text)

        instancia_processo = selector.xpath('//div[2]/header/nav/h1/text()')[0].replace(" | ", "")
        classe = selector.xpath('//div[@id="classeProcesso"]/span/text()')[0]
        area = selector.xpath('//div[@id="areaProcesso"]/span//text()')[0]
        assunto = selector.xpath('//div[@id="assuntoProcesso"]//text()')[0]
        # data_distribuicao = str(
        #     selector.xpath('//div[@id="dataHoraDistribuicaoProcesso"]//text()')[0]).split('às')[0]
        desembargador = (selector.xpath('//*[@id="relatorProcesso"]//text()')[0] if
                         selector.xpath('//*[@id="relatorProcesso"]//text()') else '')
        valor_acao = (selector.xpath('//div[@id="valorAcaoProcesso"]//text()')[0] if
                      selector.xpath('//div[@id="valorAcaoProcesso"]//text()') else '')
        valor_acao = valor_acao.replace('         ', ' ')

        # Parte do processo, são: Autor, Autora, Ré e Réu...
        lista_partes_processo = []
        partes = selector.xpath('//*[@id="tableTodasPartes"]//tr')
        if not partes:
            partes = selector.xpath('//*[@id="tablePartesPrincipais"]//tr')

        for item in partes:
            nome_parte = formatar_texto([item.xpath('./td[2]//text()')[0]])
            tipo_parte = formatar_texto([item.xpath('./td[1]/span/text()')[0].upper().replace(":", "")])
            # Tirar a acentuação das partes do processo
            tipo_parte = normalize("NFD", tipo_parte).encode("ascii", "ignore").decode("utf-8")

            lista_advogados = []
            advogados = formatar_texto(item.xpath('./td[2]//text()')[1:])
            if advogados.strip() != '' and advogados.strip().__contains__('\n'):
                advogados = advogados.split("\n")
                for index in range(0, len(advogados), 2):
                    tipo_advogado = advogados[index].upper().replace("&NBSP", "")
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
            # movimentacao = {"data": data_movimentacao, "movimento": movimento}
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
                                              data_distribuicao="",
                                              autoridade_julgadora=desembargador,
                                              valor_acao=valor_acao,
                                              partes_processo=lista_partes_processo,
                                              movimentacoes_processo=lista_movimentacoes))

        return dados_coletados
