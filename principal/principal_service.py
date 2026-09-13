import shared.rabbitmq as rabbit

class Principal:
    def __init__(self):
        self.connection, self.channel = rabbit.conectar()
        rabbit.exchange_ecommercie(self.channel)
                
        self.queue_name = "fila_principal"
    # funções de manipulacao e visualizacao de pedidos
    

    def chat_usuario(self): # comunicacao com usuario via terminal
        # opcoes de iteracao: visualizar produtos, realizar pedidos, excluir pedidos, consultar pedidos e status
        # adiciono status como campo no bd? ou apenas uma variavel... a pensar
        pass


    def consumir_evento(self): # consome 5 eventos
        pass

    def publicar_evento(self): # publica 2 eventos
        pass


    # funcoes de iteracao
    def excluir_pedido():
        pass

    def realizar_pedido():
        pass

    def visualizar_pedido():
        pass

    def consultar_pedido(): # e status
        pass


def main():
    pass

if __name__ == "__main__":
    main() 