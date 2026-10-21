import sys, os
import uvicorn

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import shared.rabbitmq as rabbit
import threading
import requests

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="MS Pagamento")

produtos_por_pedido = {}
produtos_lock = threading.Lock()

class WebhookPayload(BaseModel):
    id_pedido: str
    status: str 

class Pagamento:
    def __init__(self):
        self.connection, self.channel = rabbit.conectar()
        rabbit.exchange_ecommercie(self.channel)

        self.queue_name = "fila_pagamento"

        dir = os.path.dirname(os.path.abspath(__file__))
        self.servico = "pagamento"
        self.caminho = os.path.join(dir, "private_keys", "private_key.der")
        self.caminho_publico = os.path.join(dir, "public_keys")

        self.mock_url = "http://localhost:4000/cobranca"
        self.webhook_url = "http://localhost:5001/webhook/pagamento"

    def consumir_evento(self):
        binding_keys = ["pedido.estoque_ok"]
        rabbit.binding(self.channel, self.queue_name, binding_keys, "eCommerce")
        rabbit.consumir(self.channel, self.queue_name, self.callback, self.caminho_publico)

    def publicar_evento(self, pedido, routing_key):
        rabbit.publicar(self.channel, self.servico, self.caminho, "eCommerce", routing_key, pedido) 
    
    def callback(self, ch, chave, pedido):
        id_pedido = pedido["id_pedido"]
        
        with produtos_lock:
            produtos_por_pedido[id_pedido] = pedido.get("produtos", [])
        
        payload_mock = {
            "id_pedido": id_pedido,
            "valor": pedido.get("valor", 100.0),
            "webhook_url": self.webhook_url
        }
        try:
            response = requests.post(self.mock_url, json=payload_mock, timeout=5)
            response.raise_for_status()
            checkout_url = response.json()["checkout_url"]
            self.publicar_evento(
                {"id_pedido": id_pedido, "url_pagamento": checkout_url},
                "pagamento.cobranca_criada",
            )
        except Exception as e:
            print(f"{e}")


def publicar_do_webhook(pedido, routing_key):
    svc = Pagamento()
    try:
        svc.publicar_evento(pedido, routing_key)
    finally:
        try:
            svc.connection.close()
        except Exception:
            pass
        
@app.post("/webhook/pagamento")
def receber_webhook(payload: WebhookPayload):
    status = payload.status.strip().upper()

    with produtos_lock:
        produtos = produtos_por_pedido.pop(payload.id_pedido, [])

    if status == "APROVADO":
        publicar_do_webhook(
            {"id_pedido": payload.id_pedido, "produtos": produtos},
            "pagamento.aprovado",
        )
    elif status == "RECUSADO":
        publicar_do_webhook({"id_pedido": payload.id_pedido}, "pagamento.recusado")
    else:
        return {"status": "ignorado"}
    return {"status": "sucesso"}

def iniciar_rabbitmq():
   Pagamento().consumir_evento()

def main():
    thread_rabbit = threading.Thread(target=iniciar_rabbitmq, daemon=True)
    thread_rabbit.start()

    uvicorn.run(app, host="0.0.0.0", port=5001)

if __name__ == "__main__":
    main()