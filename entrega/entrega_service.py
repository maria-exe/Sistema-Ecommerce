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

    def callback(self, dados):
        id_pedido = dados["id_pedido"]  # verificar se essa é a melhor forma para acessar os dados
        produto = dados["produto"]
        valor = dados["valor"]

        self.emite_nota(id_pedido, produto, valor)
        mensagem = self.prepara_entrega(id_pedido)
        self.publicar_evento(mensagem)

    def emitir_nota(self, pedido, produto, valor):
        n_nota = random.randint(100, 1000)
        print(f"NOTA FISCAL   n° {n_nota}\n")
        print("-------------------------------------")
        print(f"Pedido: {pedido}\nProduto: {produto}\nValor (R$): {valor}")
        print("-------------------------------------")
        
    def preparar_entrega(pedido): 
        print(f"Processo de entrega iniciada para pedido: {pedido}\n")

        mensagem = { # adicionar mais dados nessa mensagem depois
            "id_pedido": pedido
        }
        return mensagem

def main():
    entrega = Entrega()
    entrega.consumir_evento()
   
if __name__ == "__main__":
    main()