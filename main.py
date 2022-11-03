import uvicorn
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from tj_scraper.tj_al.tj_al_primeira_instancia import TJ_AL_Primeira_Isntancia
from tj_scraper.tj_al.tj_al_segunda_instancia import TJ_AL_Segunda_Isntancia
from tj_scraper.tj_ce.tj_ce_primeira_instancia import TJ_CE_Primeira_Isntancia
from tj_scraper.tj_ce.tj_ce_segunda_instancia import TJ_CE_Segunda_Isntancia

app = FastAPI()


@app.get("/al/{numero_processo}")
def buscar_processo(numero_processo: str):
    dados_coletados_primeira = TJ_AL_Primeira_Isntancia().start_requests(numero_processo)
    dados_coletados_segunda = TJ_AL_Segunda_Isntancia().start_requests(numero_processo)
    retorno = {"primeira_instancia": jsonable_encoder(dados_coletados_primeira),
               "segunda_instancia": jsonable_encoder(dados_coletados_segunda)}
    return JSONResponse(content=retorno)


@app.get("/ce/{numero_processo}")
def buscar_processo(numero_processo: str):
    dados_coletados_primeira = TJ_CE_Primeira_Isntancia().start_requests(numero_processo)
    dados_coletados_segunda = TJ_CE_Segunda_Isntancia().start_requests(numero_processo)
    retorno = {"primeira_instancia": jsonable_encoder(dados_coletados_primeira),
               "segunda_instancia": jsonable_encoder(dados_coletados_segunda)}
    return JSONResponse(content=retorno)


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
