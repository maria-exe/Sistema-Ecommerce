from fastapi import FastAPI, Query, HTTPException
from principal_functions import valida_email
from pydantic import BaseModel
import requests

# model - ver se pprecisa disso

base_url = "http://127.0.0.1:8000/"

class Pedido(BaseModel):
    id_livro: str
    # ver quais campos precisa aqui

app = FastAPI (
    title="Paper Paws", # mudar depois rs
    version="1.0.0",
    description="Escrever alguma descrição aqui!",
)

# get = bsucar dados (consultar ou ler informacoes existentes)
# post = registar um novo dado no servidor

# listar produtos disponiveis em estoque
# criar pedidos
# registrar interesse
    # parametros: email

# cancelar interesse
# @app.get("/", include_in_schema=False)
# def read_root():
#     return RedirectResponse(url="/docs")

# pesquisar quando precisa ser async

# listar produtos
@app.get("/produtos", tags=["pedido"], responses={
    200: {"description": "Consulta no estoque bem-sucedida"}, # mudar mensagens
    500: {"description": "Erro ao consultar estoque"}
})
def livros():
    # chama api de estoque que retorna todos os produtos disponiveis
    url = base_url + "/estoque" 
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

# criar pedidos
@app.post("/pedido", tags=["pedido"], response={
    200: {"description": "Pedido criado"},
    422: {"description": "Falha na requisicao"},
    500: {"description": "Erro ao criar pedido"},
})
def criar_pedido(
    id_livro: str = None,
    quantidade: int = None
):
    # publicar evento pedido_criado?
    pass

# registrar interesse, informando email e categoria
@app.post("/registro/{categoria}/{email}", tags=["pedido"])
def registro_interesse(
    email: str = Query(description="Email do cliente", example="cliente@exemplo.com"),
    categoria: str = None
):
    if not valida_email(email): # funcao de validacao de email
        raise HTTPException(status_code=422, detail="Endereço de email inválido.")
    try:
        # publica evento interesse.promocao em tal categoria e email
        pass
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {exc}")

    return {
        "mensagem": "Interesse registrado!"
    }


@app.delete("/livros/{categoria}", tags=["pedido"], response={
    200: {"description": "Pronto! Seu e-mail foi removido da nossa lista"}
})
async def cancela_interesse(
    email: str = Query(description="Email do cliente", example="cliente@exemplo.com"),
    categoria: str = None
):  
    try: 
        pass
        # cancelar_interesse(id_livro) - criar funcao
    except Exception as exc: 
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {exc}")

    return {
        "mensagem": f"Inscrição cancelada para {categoria}!"
    }