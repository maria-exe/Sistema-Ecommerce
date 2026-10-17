import requests, uvicorn, re

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from principal_service import Principal

service = Principal()
base_url = "http://localhost:8080"

class Pedido(BaseModel):
    categoria: str
    email: str

app = FastAPI (
    title="Paper Paws", 
    version="1.0.0",
    description="Escrever alguma descrição aqui!",
)

# listar produtos
@app.get("/produtos", tags=["pedido"], responses={
    200: {"description": "Consulta no estoque bem-sucedida"},
    500: {"description": "Erro ao consultar estoque"}
})
def livros():
    url = base_url + "/estoque" 
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

# criar pedidos
@app.post("/pedido", tags=["pedido"], responses={
    200: {"description": "Pedido criado"},
    422: {"description": "Falha na requisicao"},
    500: {"description": "Erro ao criar pedido"},
})
def criar_pedido(
    id_livro: str = None,
    quantidade: int = None
):
    try:
        id_pedido = service.criar_pedido()
    except Exception as exc:
        raise HTTPException(status_code=500)

    return {
        "id_pedido": id_pedido, 
        "status": "criado"
    }

# registrar interesse, informando email e categoria
@app.post("/registro/{categoria}", tags=["interesse"])
def registro_interesse(
    email: str = Query(description="Email do cliente", example="cliente@exemplo.com"),
    categoria: str = None
):
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(padrao, email): # funcao de validacao de email
        raise HTTPException(status_code=422)
    try:
        mensagem = {
            "email": email,
            "categoria": categoria
        }
        service.publicar_evento(mensagem, "interesse.promocao")

    except Exception as exc:
        raise HTTPException(status_code=500)

    return {
        "mensagem": "Interesse registrado!"
    }

# publica evento para cancelar interesse
@app.delete("/livros/{categoria}", tags=["interesse"], responses={
    200: {"description": "Cancelamento solicitado"},
    422: {"description": "E-mail inválido"}
})
def cancela_interesse(
    categoria: str,
    email: str = Query(description="Email do cliente", example="cliente@exemplo.com")
):  
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(padrao, email): # funcao de validacao de email
        raise HTTPException(status_code=422)
    try: 
        mensagem = {
            "email": email,
            "categoria": categoria
        }

        service.publicar_evento(mensagem, "interesse.cancelado")

    except Exception as exc: 
        raise HTTPException(status_code=500)

    return {
        "mensagem": f"Inscrição cancelada para {categoria}!"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)