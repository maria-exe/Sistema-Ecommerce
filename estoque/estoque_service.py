import shared.rabbitmq as rabbit
import bd.estoque_bd as bd

class Estoque:
    def __init__(self):
        self.connection, self.channel = rabbit.conectar()
        rabbit.exchange_ecommercie(self.channel)
        
        self.queue_name = "fila_estoque"

    def consumir_evento(self): # preciso dessas funoes mesmo ou simplifico?
        binding_keys = ["pedido.criado", "pedido.excluido"]

        rabbit.binding(self.channel, self.queue_name, binding_keys, "eCommerce")
        rabbit.consumir(self.channel, self.queue_name, self.callback)

    def publicar_evento(self, mensagem, routing_key):
        rabbit.publicar(self.channel, "eCommerce", routing_key, mensagem)

    def callback(self, method, body): # padronizar os parâmetros para todos os serviços depois!!
        chave = method.routing_key

        if chave == "pedido.criado":
            # verifica disponibilidade - chama funcao do bd
            # if todos produtos disponiveis:
            self.publicar_evento(body, "pedido.estoque_ok")

            # if produto nao disponivel 
            self.publicar_evento(body, "estoque.indisponivel")
    
        elif chave == "pedido.excluido":
            # reserva/baixa estoque - funcao bd   
            pass    

def main():
    estoque = Estoque()
    estoque.consumir_evento()
   
if __name__ == "__main__":
    main()
