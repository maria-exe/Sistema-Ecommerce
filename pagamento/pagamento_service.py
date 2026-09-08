import shared.rabbitmq as rabbit
import random 

def processa_pagamento():
    resultado = random.choice([True, False])
    return resultado

def callback(channel, dados):
    pedido = dados["id_pedido"]
    resultado = processa_pagamento(pedido)

    if resultado: # pedido aprovado
        routing_key = "pagamento.aprovado"
        rabbit.publicar(channel, "eCommerce", routing_key, pedido)
    else: # pedido recusado
        routing_key = "pagamento.recusado"
        rabbit.publicar(channel, "eCommerce", routing_key, pedido)

def main():
    connection, channel = rabbit.conectar()
    rabbit.exchange_ecommercie(channel)

    # consome evento de estoque e processa pagamento
    queue_name = "fila_pagamento"
    binding_keys = ["pedido.estoque_ok"]

    rabbit.binding(channel, queue_name, binding_keys, "eCommerce")
    rabbit.consumir(channel, queue_name, callback)

if __name__ == "__main__":
    main()