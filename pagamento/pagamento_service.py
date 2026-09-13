import shared.rabbitmq as rabbit
import random 

class Pagamento:
    def __init__(self):
        self.connection, self.channel = rabbit.conectar()
        rabbit.exchange_ecommercie(self.channel)

        self.queue_name = "fila_entrega"

    def consumir_evento(self):
        binding_keys = ["pagamento.aprovado"]
        rabbit.binding(self.channel, self.queue_name, binding_keys, "eCommerce")
        rabbit.consumir(self.channel, self.queue_name, self.callback)

    def publicar_evento(self, pedido, routing_key):
        rabbit.publicar(self.channel, "eCommerce", routing_key, pedido) # melhorar a mensagem de pagamento depois!

    def callback(self, dados):
        pedido = dados["id_pedido"]
        resultado = self.processa_pagamento(pedido)

        if resultado: 
            self.publicar_evento(pedido, "pagamento.aprovado")
        else: 
            self.publicar_evento(pedido, "pagamento.recusado")

    def processa_pagamento(self):
        return random.choice([True, False])

def main():
    pagamento = Pagamento()
    pagamento.consumir_evento()

if __name__ == "__main__":
    main()