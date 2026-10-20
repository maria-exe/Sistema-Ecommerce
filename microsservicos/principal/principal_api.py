import requests, uvicorn, re
import asyncio

from fastapi import FastAPI, Query, HTTPException
from fastapi.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field
from principal_service import Principal
from estado import clientes_sse

service = Principal()
base_url = "http://localhost:8080" # estoque

app = FastAPI (
    title="Palavra Sete", 
    version="1.0.0",
    description="API do Sebo Palavra Sete",
)

# liberar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# modelos dos dados
class ItemPedido(BaseModel):
    id_livro: str
    quantidade: int = Field(gt=0)      

class NovoPedido(BaseModel):
    produtos: list[ItemPedido]

class Interesse(BaseModel):
    email: str
    categorias: list[str]

class CancelaInteresse(BaseModel):
    email: str
    categorias: list[str] = []

# verifica validade do email
def valida_email(email): 
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if (re.match(padrao, email)):
        return True
    else:
        return False
    
# Endpoints das API
# consulta produtos do endpoint de estoque
@app.get("/produtos", tags=["pedido"], responses={
    200: {"description": "Consulta no estoque bem-sucedida"},
    500: {"description": "Erro ao consultar estoque"}
})
def livros():
    url = base_url + "/estoque" # endpoint

    try: 
        response = requests.get(url)
        response.raise_for_status()
        
        if response.status_code == 200:
            return response.json()
        
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Erro ao consultar estoque")

# cria pedidos
@app.post("/pedido", tags=["pedido"], responses={
    200: {"description": "Pedido criado"},
    500: {"description": "Erro ao criar pedido"},
})
def criar_pedido(dados: NovoPedido):
    produtos = [p.model_dump() for p in dados.produtos]
    
    try:
        id_pedido = service.criar_pedido(produtos)
    except Exception as exc:
        raise HTTPException(status_code=500)

    return {
        "id_pedido": id_pedido, 
        "status": "criado"
    }

# cancela pedido - precisa corrigir ainda
@app.delete("/pedido/cancela/{id_pedido}", tags=["pedido"], responses={
    200: {"description": "Pedido cancelado"}
})
def cancela_pedido(id_pedido: str):
    try:
        service.cancela_pedido(id_pedido)
    except Exception as exc: 
        raise HTTPException(status_code=500)

    return {
        "mensagem": "Pedido cancelado"
    }

# registra interesse, informando email e categoria
@app.post("/registro", tags=["interesse"], responses={
    200: {"description": "Interesse registrado"},
    422: {"description": "E-mail invalido"},
    500: {"description": "Erro ao registrar interesse"},
})
def registro_interesse(dados: Interesse):
    if not valida_email(dados.email):
        raise HTTPException(status_code=422)
    try:
        mensagem = { "email": dados.email, "categorias": dados.categorias}
        service.publicar_evento(mensagem, "interesse.promocao") # publica interesse.promocao

    except Exception as exc:
        raise HTTPException(status_code=500)

    return { "mensagem": "Interesse registrado!" }

# publica evento para cancelar interesse
@app.post("/registro/cancela", tags=["interesse"], responses={
    200: {"description": "Cancelamento solicitado"},
    422: {"description": "E-mail invalido"}
})
def cancela_interesse(dados: CancelaInteresse):  
    if not valida_email(dados.email):
        raise HTTPException(status_code=422)
    try: 
        mensagem = { "email": dados.email, "categorias": dados.categorias}
        service.publicar_evento(mensagem, "interesse.cancelado") # publica interesse.cancelado

    except Exception as exc: 
        raise HTTPException(status_code=500)

    return {
        "mensagem": f"Interesse cancelado para {dados.categorias}!"
    }

@app.get("/sse/{id_pedido}", response_class=EventSourceResponse)
async def sse_status(id_pedido):
    async def event_generator():
        fila_cliente = asyncio.Queue()

        if id_pedido not in clientes_sse:
            clientes_sse[id_pedido] = []
        clientes_sse[id_pedido] = []

        try: 
            status_pedido = await fila_cliente.get()
            yield f"data: {status_pedido}\n\n"

        finally:
            if id_pedido in clientes_sse and fila_cliente in clientes_sse[id_pedido]:
                clientes_sse[id_pedido].remove(fila_cliente)
            if not clientes_sse.get(id_pedido):
                clientes_sse.pop(id_pedido, None)

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)