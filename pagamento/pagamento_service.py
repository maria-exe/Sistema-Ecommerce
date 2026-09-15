import shared.rabbitmq as rabbit
import random 

class Pagamento:
    def __init__(self):
        self.connection, self.channel = rabbit.conectar()
        rabbit.exchange_ecommercie(self.channel)

        self.queue_name = "fila_pagamento"

    def consumir_evento(self):
        binding_keys = ["pedido.estoque_ok"]
        rabbit.binding(self.channel, self.queue_name, binding_keys, "eCommerce")
        rabbit.consumir(self.channel, self.queue_name, self.callback)

    def publicar_evento(self, pedido, routing_key):
        rabbit.publicar(self.channel, "eCommerce", routing_key, pedido) 

    def callback(self, ch, chave, pedido):
        id_pedido = pedido["id_pedido"]
        resultado = self.processa_pagamento(id_pedido)

        if resultado: 
            print(f"\nPagamento aprovado para pedido {id_pedido}")
            self.publicar_evento(pedido, "pagamento.aprovado")
        else: 
            print(f"\nPagamento recusado para pedido {id_pedido}")
            self.publicar_evento(pedido, "pagamento.recusado")

    def processa_pagamento(self, id_pedido):
        print(f"\nProcessando pagamento do pedido: {id_pedido}\n")
        return random.choice([True, False])

def main():
    pagamento = Pagamento()
    pagamento.consumir_evento()

if __name__ == "__main__":
    main()