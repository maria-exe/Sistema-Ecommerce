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

    def callback(self, method, body): # padronizar os parâmetros para todos os serviços depois!!
        chave = method.routing_key
        # vai receber uma lista de livros como pedido ou livro individual? deve depender da implementacao do principal
        # precisa implementar a variavel de pedidos pegando os dados do body aqui
        if chave == "pedido.criado":
            temEstoque = bd.verifica_estoque(pedidos) # passa os itens como parâmetri
            # verifica disponibilidade - chama funcao do bd
            if(temEstoque):
                self.publicar_evento(body, "pedido.estoque_ok") # todos os produtos precisam estar disponíveis!
            else:  # caso não tenho produto disponível  
                self.publicar_evento(body, "estoque.indisponivel") # pedido nao pode ser antendido
           
        elif chave == "pedido.excluido":
            bd.devolver_produto(pedidos) # so chama funcao, e nao publica nada  

def main():
    estoque = Estoque()
    estoque.consumir_evento()
   
if __name__ == "__main__":
    main()