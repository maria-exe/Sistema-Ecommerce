from fastapi import FastAPI
from bd.estoque_bd import consulta_produtos

app = FastAPI()

@app.get("/estoque", summary="Base de dados dos livros do Paper Paws")
async def produtos_estoque():
    return consulta_produtos()