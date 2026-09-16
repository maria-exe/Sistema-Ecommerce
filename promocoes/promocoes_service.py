import random, time
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import shared.rabbitmq as rabbit
# falta criotografia!
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

        routing_key = f"promocao.categoria.{produto['categoria']}"
        mensagem = {
            "dados": {
                "categoria": produto["categoria"],
                "produto": produto["nome"],
                "desconto": desconto 
            }
        }
        return routing_key, mensagem
    
    def publica_promocoes(self):
        while True: 
            routing_key, mensagem = self.gera_promocoes()
            rabbit.publicar(self.channel, "promocoes", routing_key, mensagem)
            time.sleep(3) # pausa no envio

def main(): 
    promocoes = Promocoes()
    promocoes.publica_promocoes()

if __name__ == "__main__":
    main()