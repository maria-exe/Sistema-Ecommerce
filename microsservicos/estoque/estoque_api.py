import uvicorn
from fastapi import FastAPI
from bd.estoque_bd import consulta_produtos

app = FastAPI(
    title="Estoque do Sebo"
)

@app.get("/estoque", tags=["estoque"], summary="produtos em estoque")
def consultar_estoque():
    produtos = consulta_produtos()

    produtos_disponiveis = [
        {
            "id": produto[0],
            "titulo": produto[1],
            "autor": produto[2],
            "categoria": produto[3],
            "preco": produto[4], 
            "quantidade": produto[5]
        }
        for produto in produtos
    ]
    return {
        "produtos": produtos_disponiveis
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)