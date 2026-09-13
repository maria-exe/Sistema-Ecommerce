import shared.rabbitmq as rabbit

# vai precisar verificar assinatura digital aqui!!
def callback(channel, dados):
    promocao = dados["dados"]
    print(f"PROMOÇÃO! {promocao['produto']} com {promocao['desconto']}% de desconto! [{promocao['categoria']}]")
   
def main():
    connection, channel = rabbit.conectar()
    rabbit.exchange_promocoes(channel)

    queue_name = "fila_c1"
    binding_keys = ["promocao.categoria.*"] # tem interesse em todas as categorias

    rabbit.binding(channel, queue_name, binding_keys, "promocoes")
    rabbit.consumir(channel, queue_name, callback)

if __name__ == "__main__":
    main()