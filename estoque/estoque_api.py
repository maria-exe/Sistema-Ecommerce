from fastapi import FastAPI
from .bd.estoque_bd import consulta_produtos

app = FastAPI("Estoque do Paper Paws")

@app.get("/estoque", summary="produtos em estoque")
def consultar_estoque():
    produtos = consulta_produtos()

    produtos_disponiveis = [
        {
            "id_produto": produto[0],
            "nome": produto[1],
            "categoria": produto[2],
            "preco": produto[3],
            "estoque": produto[4]
        }
        for produto in produtos
    ]

    return {
        "produtos": produtos_disponiveis
    }