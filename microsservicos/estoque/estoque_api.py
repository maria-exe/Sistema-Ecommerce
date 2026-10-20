import uvicorn
from fastapi import FastAPI, HTTPException
from bd import estoque_bd as bd

app = FastAPI(
    title="Estoque da Palavra Sete",
    description="API dos produtos em estoque da sebo Palavra Sete"
)

@app.get("/estoque", tags=["estoque"], summary="produtos em estoque")
def consultar_estoque():
    try: 
        produtos = bd.consulta_produtos() # consulta produtos em estoque
        produtos_disponiveis = [
            {
                "id": produto[0],
                "titulo": produto[1],
                "autor": produto[2],
                "categoria": produto[3],
                "preco": produto[4], 
                "quantidade": produto[5],
                "capa": produto[6]
            }
            for produto in produtos
        ]
        return {
            "produtos": produtos_disponiveis # retorna eles no json
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao acessar banco de dados")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)