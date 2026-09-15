import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import shared.rabbitmq as rabbit
import random

# nao esquecer de adicionar criptografia
class Entrega: 
    def __init__(self):
        self.connection, self.channel = rabbit.conectar()
        rabbit.exchange_ecommercie(self.channel)

        self.queue_name = "fila_entrega"

    def consumir_evento(self):
        binding_keys = ["pagamento.aprovado"]

        rabbit.binding(self.channel, self.queue_name, binding_keys, "eCommerce")
        rabbit.consumir(self.channel, self.queue_name, self.callback)

    def publicar_evento(self, mensagem):
        rabbit.publicar(self.channel, "eCommerce", "pedido.enviado", mensagem)    

    def callback(self, ch, chave, dados):
        id_pedido = dados["id_pedido"]  # verificar se essa é a melhor forma para acessar os dados
        produtos = dados["produtos"]

        print(f"\nPedido: {id_pedido} recebido.")

        self.emitir_nota(id_pedido, produtos)
        mensagem = self.preparar_entrega(id_pedido)
        self.publicar_evento(mensagem)

        print(f"\nPedido: {id_pedido} enviado.")

    def emitir_nota(self, pedido, produtos):
        n_nota = random.randint(100, 1000)
        print(f"\nNOTA FISCAL   n° {n_nota}\n")
        print("-------------------------------------")
        print(f"Pedido: {pedido}")
        for item in produtos:
            print(f"Livro: {item['id_livro']} | Quantidade: {item['quantidade']}")
        print("-------------------------------------")
        
    def preparar_entrega(self, pedido): 
        print(f"Processo de entrega iniciada para pedido: {pedido}\n")

        mensagem = { 
            "id_pedido": pedido
        }
        return mensagem

def main():
    entrega = Entrega()
    entrega.consumir_evento()
   
if __name__ == "__main__":
    main()