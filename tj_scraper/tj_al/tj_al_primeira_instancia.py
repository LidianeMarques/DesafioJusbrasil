from scrap.scrap_primeira_instancia import ScrapPrimeiraInstancia


class TJ_AL_Primeira_Isntancia(ScrapPrimeiraInstancia):
    url_base = 'https://www2.tjal.jus.br'

    def start_requests(self, numero_processo):
        return super(TJ_AL_Primeira_Isntancia, self).start_requests(numero_processo)

    def parse(self, response, **kwargs):
        return super(TJ_AL_Primeira_Isntancia, self).parse(response, **kwargs)