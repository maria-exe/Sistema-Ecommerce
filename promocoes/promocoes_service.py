import random, time
import shared.rabbitmq as rabbitmq

produtos = [
    {"nome": "O retrato de Dorian Gray", "categoria": "livros"},
    {"nome": "Cosmos", "categoria": "livros"},
    {"nome": "Notebook Lenovo", "categoria": "tecnologia"},
    {"nome": "Samsung Tab S10 Lite", "categoria": "tecnologia"},
    {"nome": "Camiseta CottonOn Preta", "categoria": "roupas"},
    {"nome": "Moletom", "categoria": "roupas"},
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
    connection, channel = rabbitmq.conectar()
    rabbitmq.exchange_promocoes(channel)

    while True:
        mensagem = promocoes()
        rabbitmq.publicar(channel, 'promocoes', mensagem["routing_key"], mensagem)
        time.sleep(5)

if __name__ == "__main__":
   main()