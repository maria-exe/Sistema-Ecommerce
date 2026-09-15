import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import shared.rabbitmq as rabbit
import bd.estoque_bd as bd

class Estoque:
    def __init__(self):
        self.connection, self.channel = rabbit.conectar()
        rabbit.exchange_ecommercie(self.channel)
        
        self.queue_name = "fila_estoque"

    def consumir_evento(self):
        binding_keys = ["pedido.criado", "pedido.excluido"]

        rabbit.binding(self.channel, self.queue_name, binding_keys, "eCommerce")
        rabbit.consumir(self.channel, self.queue_name, self.callback)

    def publicar_evento(self, mensagem, routing_key):
        rabbit.publicar(self.channel, "eCommerce", routing_key, mensagem)

    def callback(self, ch, chave, mensagem):
        livros_pedidos = mensagem["produtos"]
        id_pedido = mensagem["id_pedido"]

        print(f"Pedido {id_pedido} recebido.")
        
        if chave == "pedido.criado":
            temEstoque = bd.verificar_estoque(livros_pedidos)
            
            if temEstoque: # verifica disponibilidade
                bd.reservar_produto(livros_pedidos)
                print(f"Pedido {id_pedido} em estoque, reservado")
                self.publicar_evento(mensagem, "pedido.estoque_ok") 
            else:   
                print(f"Pedido {id_pedido} indisponivel\n")
                self.publicar_evento(mensagem, "estoque.indisponivel") 
           
        elif chave == "pedido.excluido":
            motivo = mensagem.get("motivo", "")
            if motivo != "estoque.indisponivel":
                bd.devolver_produto(livros_pedidos) 
                print(f"Pedido {id_pedido} cancelado. Produtos devolvidos ao estoque.")
            else:
                print(f"Pedido {id_pedido} excluido por falta de estoque.")

def main():
    estoque = Estoque()
    estoque.consumir_evento()
   
if __name__ == "__main__":
    main()