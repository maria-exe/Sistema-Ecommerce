import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shared.rabbitmq as rabbit
import uuid
import threading 

class Principal:
    def __init__(self):
        self.publica_connection, self.publica_channel = rabbit.conectar()
        rabbit.exchange_ecommercie(self.publica_channel)  

        self.queue_name = "fila_principal"

        dir = os.path.dirname(os.path.abspath(__file__))
        self.servico = "principal"
        self.caminho = os.path.join(dir, "private_keys", "private_key.der")
        self.caminho_publico = os.path.join(dir, "public_keys")

        self.pedidos_lock = threading.Lock()
        self.pedidos = {}
   
    def consumir_evento(self): #
        self.consome_connection, self.consome_channel = rabbit.conectar()
        rabbit.exchange_ecommercie(self.consome_channel)

        binding_keys = ["pagamento.aprovado", "pagamento.recusado", "pedido.enviado", "pedido.estoque_ok", "estoque.indisponivel"]
        
        rabbit.binding(self.consome_channel, self.queue_name, binding_keys, "eCommerce")
        rabbit.consumir(self.consome_channel, self.queue_name, self.callback, self.caminho_publico)

    def publicar_evento(self, mensagem, routing_key, canal=None): 
        canal_usado = canal if canal else self.publica_channel
        rabbit.publicar(canal_usado, self.servico, self.caminho, "eCommerce", routing_key, mensagem)

    # funcoes de iteracao
    def excluir_pedido(self, id_pedido):        
        with self.pedidos_lock:
            if id_pedido not in self.pedidos:
                print("Pedido não encontrado.")
                return

            status_atual = self.pedidos[id_pedido]["status"]
            if "excluido" in status_atual:
                print(f"\nO pedido {id_pedido} ja foi excluido.")
                return
            
            produtos = self.pedidos[id_pedido]["produtos"]
            self.pedidos[id_pedido]["status"] = "excluido"

        mensagem = {
            "id_pedido": id_pedido,
            "produtos": produtos
        }

        self.publicar_evento(mensagem, "pedido.excluido", self.publica_channel)
        print(f"\nPedido {id_pedido} excluido")

    def realizar_pedido(self): # modificar funcao para aceitar parametros recebidos da api
        livros = []
        while True: # interacao para escolher usuario
            self.visualizar_produto()
            livro = input("\nDigite o id do livro desejado (ou sair para encerrar): ")

            if livro.lower() == "sair":
                break

            quantidade = int(input("\nQuantidade: "))
            livros.append({"id_livro": livro, "quantidade": quantidade})

        if not livros:
            print("Nenhum produto selecionado.")
            return

        id_pedido = str(uuid.uuid4())[:8] 

        mensagem = {
            "id_pedido": id_pedido,
            "produtos": livros
        }

        with self.pedidos_lock:
            self.pedidos[id_pedido] = {"status": "criado", "produtos": livros}

        # self.publicar_evento(mensagem, "pedido.criado", self.publica_channel)
        # print(f"Pedido {id_pedido} enviado. Para consulta status, acesse o menu.")

    def consultar_pedido(self):
        with self.pedidos_lock: 
            if not self.pedidos:
                print("Você ainda não tem pedidos!")
            for id_pedido, pedido in self.pedidos.items():
                print(f"Pedido: {id_pedido} | Status: {pedido['status']}")

    # atualiza status e envia evento para excluir pedido
    def callback(self, ch, chave, mensagem):
        id_pedido = mensagem["id_pedido"]

        with self.pedidos_lock:

            if id_pedido not in self.pedidos:
                print(f"\nEvento para pedido desconhecido {id_pedido}, ignorando.")
                return
            if chave == "pagamento.aprovado":
                self.pedidos[id_pedido]["status"] = "pagamento aprovado"
            elif chave == "pedido.enviado":
                self.pedidos[id_pedido]["status"] = "pedido enviado"
            elif chave == "pedido.estoque_ok":
                self.pedidos[id_pedido]["status"] = "pedido em estoque"
            elif chave == "estoque.indisponivel":
                self.pedidos[id_pedido]["status"] = "pedido excluido por estoque indisponivel"
            elif chave == "pagamento.recusado":
                self.pedidos[id_pedido]["status"] = "pedido excluido por falha no pagamento"


            if chave in ["estoque.indisponivel", "pagamento.recusado"]:
                produtos = self.pedidos[id_pedido]["produtos"]
                mensagem_exclusao = {
                    "id_pedido": id_pedido,
                    "produtos": produtos,
                    "motivo": chave 
                }
                self.publicar_evento(mensagem_exclusao, "pedido.excluido", ch)

def main():
    principal = Principal()
    thread_eventos = threading.Thread(target=principal.consumir_evento, daemon=True)
    thread_eventos.start()

    principal.chat_usuario()
if __name__ == "__main__":
    main() 