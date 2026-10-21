import uuid
import requests
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

cobrancas = {}

app = FastAPI(
    title="Mock de Pagamento Externo"
)

class CriarCobrancaRequest(BaseModel):
    id_pedido: str
    valor: float
    webhook_url: str

@app.post("/cobranca")
def criar_cobranca(req: CriarCobrancaRequest):
    cobranca_id = str(uuid.uuid4())[:8]
    
    cobrancas[cobranca_id] = {
        "id_pedido": req.id_pedido,
        "valor": req.valor,
        "webhook_url": req.webhook_url
    }
    
    checkout_url = f"http://localhost:4000/checkout/{cobranca_id}"
    return {"cobranca_id": cobranca_id, "checkout_url": checkout_url}

@app.get("/checkout/{cobranca_id}", response_class=HTMLResponse)
def pagina_checkout(cobranca_id: str):
    if cobranca_id not in cobrancas:
        raise HTTPException(status_code=404, detail="Cobrança não encontrada")
    
    cobranca = cobrancas[cobranca_id]
    
    return f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <title>Mock de Pagamento</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 60px; background-color: #f4f4f9; }}
            .card {{ background: white; padding: 30px; display: inline-block; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
            .btn {{ padding: 12px 24px; margin: 10px; font-size: 16px; border: none; cursor: pointer; border-radius: 5px; color: white; }}
            .btn-approve {{ background-color: #28a745; }}
            .btn-reject {{ background-color: #dc3545; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Simulador de Checkout</h2>
            <p><strong>ID do Pedido:</strong> {cobranca['id_pedido']}</p>
            <p><strong>Valor Total:</strong> R$ {cobranca['valor']:.2f}</p>
            <hr>
            <p>Escolha o resultado do pagamento:</p>
            <form action="/checkout/{cobranca_id}/processar" method="post">
                <button type="submit" name="status" value="APROVADO" class="btn btn-approve">Pagamento Aprovado</button>
                <button type="submit" name="status" value="RECUSADO" class="btn btn-reject">Pagamento Recusado</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/checkout/{cobranca_id}/processar", response_class=HTMLResponse)
def processar_pagamento(cobranca_id: str, status: str = Form(...)):
    if cobranca_id not in cobrancas:
        raise HTTPException(status_code=404, detail="Cobrança não encontrada")
    
    cobranca = cobrancas.pop(cobranca_id)
    payload = {
        "id_pedido": cobranca["id_pedido"],
        "status": status
    }

    try:
        requests.post(cobranca["webhook_url"], json=payload, timeout=5)
        mensagem_envio = "Pagamento aprovado com sucesso!"
    except Exception as e:
        mensagem_envio = f"Erro ao chamar o Webhook: {str(e)}"

    return f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head><meta charset="UTF-8"><title>Pagamento Concluído</title></head>
    <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 60px;">
        <h2>Resultado: Pagamento {status}</h2>
        <p>{mensagem_envio}</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)