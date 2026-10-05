from fastapi import FastAPI, Query, HTTPException
from gateaway_functions import valida_email, registra
from pydantic import BaseModel

# model - ver se pprecisa disso
class Pedido(BaseModel):
    id_livro: str
    # ver quais campos precisa aqui

app = FastAPI (
    title="Paper Paws", # mudar depois rs
    version="1.0.0",
    description="",
)

# get = bsucar dados (consultar ou ler informacoes existentes)
# post = registar um novo dado no servidor

# listar produtos disponiveis em estoque
# criar pedidos
# registrar interesse
    # parametros: email

# cancelar interesse


# listar produtos
@app.get("/produtos", responses={
    200: {"description": "Lista de produtos"},
    422: {"description": "Lista de produtos"},
    500: {"description": "Lista de produtos"},
})
async def livros(
    livro: Pedido 
):
    # chama api de estoque
    return {"message": "Eita mundo!"}

@app.post("/pedido")
async def criar_pedido():
    pass

@app.post("/registro/{id_livro}")
async def registro_interesse(
    email: str = Query(description="Email do cliente", example="cliente@exemplo.com"),
    id_livro: str = None
):
    if not valida_email(email):
        raise HTTPException(status_code=422, detail="Endereço de email inválido.")
    try: 
        registra(id_livro) # criar funcao que registra interesse
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {exc}")

    return {
        "mensagem": "Interesse registrado!"
    }

@app.delete("/livros/{id_livro}")
async def cancela_interesse(
    email: str = Query(description="Email do cliente", example="cliente@exemplo.com"),
    id_livro: str = None
):  
    try: 
        cancelar_interesse(id_livro) # criar funcao
    except Exception as exc: 
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {exc}")

    return {
        "mensagem": f"Inscrição cancelada para {id_livro}!"
    }