import random, time
import shared.rabbitmq as rabbit

produtos = [
    {"nome": "O Retrato de Dorian Gray", "categoria": "romance"}, # categoria A
    {"nome": "O Hobbit", "categoria": "romance"},
    {"nome": "A Figura", "categoria": "terror"},  # categoria B
    {"nome": "Misery", "categoria": "terror"}, 
    {"nome": "Joy", "categoria": "quadrinhos"}, # categoria C
    {"nome": "Define The Relationship", "categoria": "quadrinhos"},
]

class Promocoes: 
    def __init__(self):
        self.connection, self.channel = rabbit.conectar()
        rabbit.exchange_promocoes(self.channel)

    def gera_promocoes(self):
        produto = random.choice(produtos)
        desconto = random.randint(5, 90)

        return {  # verificar isso depois
            "routing_key": f"promocao.categoria.{produto['categoria']}",
            "dados": {
                "categoria": produto["categoria"],
                "produto": produto["nome"],
                "desconto": desconto 
            }
        }
    
    def publica_promocoes(self):
        while True: 
            mensagem = self.gera_promocoes()
            rabbit.publicar(self.channel, "promocoes", mensagem["routing_key"], mensagem) # padronizar esse routing key depois
            time.sleep(3) # pausa no envio

def main(): 
    promocoes = Promocoes()
    promocoes.publica_promocoes()

if __name__ == "__main__":
    main()
