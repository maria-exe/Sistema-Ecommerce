import shared.rabbitmq as rabbit
import random 


def emitir_nota(pedido, produto, valor): # frescurada minha rs
    n_nota = random.randint(100, 1000)
    print(f"NOTA FISCAL   n° {n_nota}\n")
    print("-------------------------------------")
    print(f"Pedido: {pedido}\nProduto: {produto}\nValor (R$): {valor}")
    print("-------------------------------------")

def preparar_entrega(pedido): 
    print(f"Processo de entrega iniciada para pedido: {pedido}\n")

def callback(channel, dados):
    
    pedido =  dados["pedido"]
    produto = dados["produto"]
    valor = dados["valor"]

    # operacoes de emissao e entrega
    emitir_nota(pedido, produto, valor)
    preparar_entrega(pedido)

    # melhorar isso depois
    mensagem = {
        "dados": {
            "pedido": pedido
        }}
    
    rabbit.publicar(channel, "eCommerce", "pedido.enviado", mensagem)

    pass

def main():
    connection, channel = rabbit.conectar()
    rabbit.exchange_ecommercie(channel)

    queue_name = "fila_entrega"
    binding_keys = ["pagamento.aprovado"]

    rabbit.binding(channel, queue_name, binding_keys, "eCommerce")
    rabbit.consumir(channel, queue_name, callback)

if __name__ == "__main__":
    main()