import random, time
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import shared.rabbitmq as rabbit


# consumir consulta o endpoint do estoque para gerar promocoes apenas de produtos em estoque
# consome o evento interesse.promocao
class Promocoes: 
    def __init__(self):
        self.connection, self.channel = rabbit.conectar()
        rabbit.exchange_promocoes(self.channel)

        dir_atual = os.path.dirname(os.path.abspath(__file__))
        self.servico = "promocoes"
        self.caminho_privado = os.path.join(dir_atual, "private_keys", "private_key.der")


    # requisito: consome o evento interesse.promocao
    def consumir_evento(self):
        binding_keys = ["interesse.promocao"]
        rabbit.binding(self.channel, self.queue_name, binding_keys, "eCommerce")
        rabbit.consumir(self.channel, self.queue_name, self.callback, self.caminho_publico)


    # def gera_promocoes(self):
    #     produto = random.choice(produtos)
    #     desconto = random.randint(5, 90)

    #     routing_key = f"promocao.categoria.{produto['categoria']}"
    #     mensagem = {
    #         "dados": {
    #             "categoria": produto["categoria"],
    #             "produto": produto["nome"],
    #             "desconto": desconto 
    #         }
    #     }
    #     return routing_key, mensagem
    
    # def publica_promocoes(self):
    #     while True: 
    #         routing_key, mensagem = self.gera_promocoes()
    #         rabbit.publicar(self.channel, self.servico, self.caminho_privado, "promocoes", routing_key, mensagem)
    #         time.sleep(3) # pausa no envio

def main(): 
    promocoes = Promocoes()
    promocoes.publica_promocoes()

if __name__ == "__main__":
    main()