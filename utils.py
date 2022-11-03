""""
    Arquivo de funções auxiliares
"""


def formatar_texto(lista_texto):
    lista_texto = [x.replace("\t", "").replace("\n", "").strip() for x in lista_texto]
    texto = "\n".join(list(filter(lambda x: x != '', lista_texto)))
    return texto
