from scrap.scrap_segunda_instancia import ScrapSegundaInstancia


class TJ_CE_Segunda_Isntancia(ScrapSegundaInstancia):
    url_base = 'https://esaj.tjce.jus.br'

    def start_requests(self, numero_processo):
        return super(TJ_CE_Segunda_Isntancia, self).start_requests(numero_processo)

    def parse(self, response, **kwargs):
        return super(TJ_CE_Segunda_Isntancia, self).parse(response, **kwargs)
