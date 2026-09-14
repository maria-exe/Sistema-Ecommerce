import shared.rabbitmq as rabbit
import threading 

# adicionar um dicionario que representa o catalogo com os livros disponiveis para compra
catalogo = [ # o que vai mostrar de opcoes para o usuario - tem os mesmos no bd com seu respectivo estoque
    {"titulo": "O Retrato de Dorian Gray"},
    {"titulo": "Atelier of Witch"},
    {"titulo": "Vidas Secas"},
    {"titulo": "Misery"},
    {"titulo": "Mrs. Dalloway"}
]

class Principal:
    def __init__(self):
        self.connection, self.channel = rabbit.conectar() # tá errado por enquanto! vamos precisar de duas conexões, uma para receber e outra para publicar!!
        self.queue_name = "fila_principal"
        rabbit.exchange_ecommercie(self.channel)
   
    
    # funções de manipulacao e visualizacao de pedidos
    def chat_usuario(self): # comunicacao com usuario via terminal
        print("============================")
        print("1. Visualizar catálogo de livros")
        print("2. Realizar pedidos")
        print("3. Excluir pedidos")
        print("4. Consultar pedidos")
        print("5. Encerrar atendimento")
        print("============================")

        escolha = input("Digite: ")
        match escolha:
            case "1":
                self.visualizar_produto()
                # mostra escolhas - tipo selecione o id do produto desejado
            case "2":
                self.realizar_pedido()
            case "3":
                self.excluir_pedido()
            case "4":
                self.consultar_pedido()
            case "5":
            case _:
                return "Entrada invalida"
        # opcoes de iteracao: visualizar produtos, realizar pedidos, excluir pedidos, consultar pedidos e status
        # adiciono status como campo no bd? ou apenas uma variavel... a pensar


        # usar match case
        pass

    def consumir_evento(self): # consome 5 eventos
        binding_keys = ["pagamento.aprovado", "pagamento.recusado", "pedido.enviado", "pedido.estoque_ok", "estoque.indisponivel"]
        
        abbit.binding(self.channel, self.queue_name, binding_keys, "eCommerce")
        rabbit.consumir(self.channel, self.queue_name, self.callback)

    def publicar_evento(self, mensagem, routing_key): # publica 2 eventos: pedido.criado e pedido.excluido
        rabbit.publicar(self.channel, "eCommerce", routing_key, mensagem)


    # funcoes de iteracao
    def excluir_pedido(self):
        # mensagem que pedido foi excluido
        print(f"Pedido {alguma_coisa} excluido") # tipo id do pedido
        # monta mensagem com dados dos pedidos para publicar
        # publica evento
        rabbit.publicar(canal, "eCommerce", mensagem, "pedido.excluido") # publico aqui ou dentro de chat_usuario?

    def realizar_pedido(self):
        # interecao de escolha de quais produtos o usuario quer
        # montar mensagem
        # deve ter: identificador do pedido, os produtos, quantidades e informações necessárias para o processamento do pedido.
        # chamar poublicar eventos com a routing key: pedido.criado
        pass

    def visualizar_produto(self):
        # mostra os produtos disponiveis - o dicionario que criei no inicio do arquivo
        pass

    def consultar_pedido(self): # e status
        # mostrar pedidos feitos pelo usuario
        pass

    def callback(self):
        # resposta a cada evento consumido
        pass


def main():
    pass

if __name__ == "__main__":
    main() 