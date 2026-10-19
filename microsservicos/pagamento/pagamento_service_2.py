import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import shared.rabbitmq as rabbit
import threading
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

#agora o ms pagamento tem q virar um server http
app = FastAPI(title="MS Pagamento")

# Instância global para publicar eventos a partir da rota de Webhook
pagamento_service = None

class WebhookPayload(BaseModel):
    id_pedido: str
    status: str  #aprovado ou recusado

class Pagamento:
    def __init__(self):
        self.connection, self.channel = rabbit.conectar()
        rabbit.exchange_ecommercie(self.channel)

        self.queue_name = "fila_pagamento"

        dir = os.path.dirname(os.path.abspath(__file__))
        self.servico = "pagamento"
        self.caminho = os.path.join(dir, "private_keys", "private_key.der")
        self.caminho_publico = os.path.join(dir, "public_keys")

    def consumir_evento(self):
        binding_keys = ["pedido.estoque_ok"]
        rabbit.binding(self.channel, self.queue_name, binding_keys, "eCommerce")
        rabbit.consumir(self.channel, self.queue_name, self.callback, self.caminho_publico)

    def publicar_evento(self, pedido, routing_key):
        rabbit.publicar(self.channel, self.servico, self.caminho, "eCommerce", routing_key, pedido) 
    
    # quando o estoque confirma, solicita a cobrança ao Mock
    def callback(self, ch, chave, pedido):
        id_pedido = pedido["id_pedido"]
        print(f"\n[MS Pagamento] Pedido {id_pedido} recebido do estoque. Solicitando cobrança ao Mock...")

        payload_mock = {
            "id_pedido": id_pedido,
            "valor": pedido.get("valor", 100.0),
            "webhook_url": self.webhook_url
        }
    try:
        response = requests.post(self.mock_url, json=payload_mock, timeout=5)
        if response.status_code == 200:
            print(f"[MS Pagamento] Cobrança registada no Mock para o pedido {id_pedido}.")
        else:
            print(f"[MS Pagamento] Erro no Mock: {response.text}")
    except Exception as e:
        print(f"[MS Pagamento] Falha ao conectar ao Mock de Pagamento: {e}")
    
#endpoint q recebe o webhook enviado pelo mock
@app.post("/webhook/pagamento")
def receber_webhook(payload: WebhookPayload):
    print(f"\n[MS Pagamento] Webhook recebido! Pedido: {payload.id_pedido} | Status: {payload.status}")
    
    pedido = {"id_pedido": payload.id_pedido}
    
    if payload.status.upper() == "APROVADO":
        pagamento_service.publicar_evento(pedido, "pagamento.aprovado")
        print(f"[MS Pagamento] Evento 'pagamento.aprovado' publicado no RabbitMQ.")
    else:
        pagamento_service.publicar_evento(pedido, "pagamento.recusado")
        print(f"[MS Pagamento] Evento 'pagamento.recusado' publicado no RabbitMQ.")
        
    return {"status": "sucesso"}

def iniciar_rabbitmq():
    global pagamento_service
    pagamento_service = Pagamento()
    pagamento_service.consumir_evento()

def main():
    # rabbitmq em thread secundária
    thread_rabbit = threading.Thread(target=iniciar_rabbitmq, daemon=True)
    thread_rabbit.start()

    #servidor fastapi 
    uvicorn.run(app, host="0.0.0.0", port=5001)

if __name__ == "__main__":
    main()