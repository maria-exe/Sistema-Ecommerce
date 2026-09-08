import random, time
import shared.rabbitmq as rabbit

produtos = [
    {"nome": "O retrato de Dorian Gray", "categoria": "livros"}, # categoria A
    {"nome": "Cosmos", "categoria": "livros"},
    {"nome": "Notebook Lenovo", "categoria": "tecnologia"},  # categoria B
    {"nome": "Samsung Tab S10 Lite", "categoria": "tecnologia"}, 
    {"nome": "Caderno 10 matérias", "categoria": "papelaria"}, # categoria C
    {"nome": "Caneta Bic", "categoria": "papelaria"},
]

def promocoes():
    produto = random.choice(produtos)
    desconto = random.randint(5, 90)

    return { 
    "routing_key": f"promocao.categoria.{produto['categoria']}",
    "dados": {
        "categoria": produto["categoria"],
        "produto": produto["nome"],
        "desconto": desconto
    }}

def main():
    connection, channel = rabbit.conectar()
    rabbit.exchange_promocoes(channel)

    while True:
        mensagem = promocoes()
        rabbit.publicar(channel, "promocoes", mensagem["routing_key"], mensagem) # padronizar esse routing key depois
        time.sleep(3)

if __name__ == "__main__":
   main()