import shared.rabbitmq as rabbit

# vai precisar verificar assinatura digital aqui!!
def callback(channel, dados):
    promocao = dados["dados"]
    print(f"[{promocao['categoria']}] PROMOÇÃO! {promocao['produto']} com {promocao['desconto']}% de desconto!")
   
def main():
    connection, channel = rabbit.conectar()
    rabbit.exchange_promocoes(channel)

    queue_name = "fila_c1"
    binding_keys = ["promocao.categoria.livros", "promocao.categoria.tecnologia"] # tem interesse na categoria A e B

    rabbit.binding(channel, queue_name, binding_keys, "promocoes")
    rabbit.consumir(channel, queue_name, callback)

if __name__ == "__main__":
    main()