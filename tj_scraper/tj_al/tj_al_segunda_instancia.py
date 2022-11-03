from scrap.scrap_segunda_instancia import ScrapSegundaInstancia


class TJ_AL_Segunda_Isntancia(ScrapSegundaInstancia):
    url_base = 'https://www2.tjal.jus.br'

    def start_requests(self, numero_processo):
        return super(TJ_AL_Segunda_Isntancia, self).start_requests(numero_processo)

    def parse(self, response, **kwargs):
        return super(TJ_AL_Segunda_Isntancia, self).parse(response, **kwargs)