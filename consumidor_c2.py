import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import shared.rabbitmq as rabbit

def callback(channel, routing_key, dados):
    promocao = dados["dados"]
    print(f"PROMOÇÃO! {promocao['produto']} com {promocao['desconto']}% de desconto! [{promocao['categoria']}]")
   
def main():
    connection, channel = rabbit.conectar()
    rabbit.exchange_promocoes(channel)

    dir_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_publico = os.path.join(dir_atual, "public_keys")

    queue_name = "fila_c1"
    binding_keys = ["promocao.categoria.*"] # tem interesse em todas as categorias

    rabbit.binding(channel, queue_name, binding_keys, "promocoes")
    rabbit.consumir(channel, queue_name, callback, caminho_publico)

if __name__ == "__main__":
    main()