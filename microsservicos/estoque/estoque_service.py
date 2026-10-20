import sys, os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import shared.rabbitmq as rabbit
from bd import estoque_bd as bd

class Estoque:
    def __init__(self):
        self.connection, self.channel = rabbit.conectar()
        rabbit.exchange_ecommercie(self.channel)
        
        self.queue_name = "fila_estoque"

        # criptografia
        dir = os.path.dirname(os.path.abspath(__file__))
        self.servico = "estoque"
        self.caminho = os.path.join(dir, "private_keys", "private_key.der")
        self.caminho_publico = os.path.join(dir, "public_keys")

    # funcoes auxiliares para publicar e consumir
    def consumir_evento(self):
        binding_keys = ["pedido.criado", "pedido.excluido"] # consome

        rabbit.binding(self.channel, self.queue_name, binding_keys, "eCommerce")
        rabbit.consumir(self.channel, self.queue_name, self.callback, self.caminho_publico)

    def publicar_evento(self, mensagem, routing_key):
        rabbit.publicar(self.channel, self.servico, self.caminho, "eCommerce", routing_key, mensagem)

    def callback(self, ch, chave, mensagem):
        livros_pedidos = mensagem["produtos"]
        id_pedido = mensagem["id_pedido"]

        if chave == "pedido.criado":
            if bd.pedido_reservado(id_pedido) or bd.reservar_pedido(id_pedido, livros_pedidos):
                self.publicar_evento(mensagem, "pedido.estoque_ok") # publica estoque ok
            
            else: 
                self.publicar_evento(mensagem, "estoque.indisponivel") # publica estoque indisponivel
        elif chave == "pedido.excluido":
            bd.devolver_pedido(id_pedido, livros_pedidos) # devolve produtos de pedidos excluidos
      
def main():
    estoque = Estoque()
    estoque.consumir_evento()
   
if __name__ == "__main__":
    main()