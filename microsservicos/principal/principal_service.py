import sys, os
import estado

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import shared.rabbitmq as rabbit
import uuid, threading 

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
   
    def consumir_evento(self): 
        self.consome_connection, self.consome_channel = rabbit.conectar()
        rabbit.exchange_ecommercie(self.consome_channel)

        # eventos consumidos
        binding_keys = ["pagamento.aprovado", "pagamento.recusado", "pedido.enviado", "pedido.estoque_ok", "estoque.indisponivel", "pagamento.cobranca_criada"]
        
        rabbit.binding(self.consome_channel, self.queue_name, binding_keys, "eCommerce")
        rabbit.consumir(self.consome_channel, self.queue_name, self.callback, self.caminho_publico)

    def publicar_evento(self, mensagem, routing_key, canal=None):
        if canal is not None:
            rabbit.publicar(canal, self.servico, self.caminho, "eCommerce", routing_key, mensagem)
            return

        conn, ch = rabbit.conectar()
        try:
            rabbit.exchange_ecommercie(ch)
            rabbit.publicar(ch, self.servico, self.caminho, "eCommerce", routing_key, mensagem)
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def cancela_pedido(self, id_pedido):        
        with self.pedidos_lock:
            pedido = self.pedidos.get(id_pedido)

            if pedido is None:
                return "nao_encontrado"

            if pedido["status"] == "excluido" or pedido["status"] == "cancelado":
                return "ja_excluido"
            
            produtos = self.pedidos[id_pedido]["produtos"]
            pedido["status"] = "excluido"

        mensagem = { "id_pedido": id_pedido, "produtos": produtos }
        self.publicar_evento(mensagem, "pedido.excluido")
 
    def criar_pedido(self, produtos):
        if not produtos:
            raise ValueError("Nenhum produto selecionado")
        
        id_pedido = str(uuid.uuid4())[:8] 
        mensagem = { "id_pedido": id_pedido, "produtos": produtos }

        with self.pedidos_lock:
            self.pedidos[id_pedido] = {"status": "criado", "produtos": produtos}
        
        self.publicar_evento(mensagem, "pedido.criado")
        return id_pedido

    # atualiza status e envia evento para excluir pedido
    def callback(self, ch, chave, mensagem):
        id_pedido = mensagem["id_pedido"]

        with self.pedidos_lock:
            if id_pedido not in self.pedidos:
                print(f"\nEvento para pedido desconhecido {id_pedido}, ignorando.")
                return

            status = ""
            if chave == "pagamento.aprovado":
                status = "pagamento aprovado"
            elif chave == "pedido.enviado":
                status = "pedido enviado"
            elif chave == "pedido.estoque_ok":
                status = "pedido em estoque"
            elif chave == "pagamento.cobranca_criada":
                status = "pagamento disponível"
            elif chave == "estoque.indisponivel":
                status = "pedido excluido por estoque indisponivel"
            elif chave == "pagamento.recusado":
                status = "pedido excluido por falha no pagamento"

            self.pedidos[id_pedido]["status"] = status

            if chave in ["estoque.indisponivel", "pagamento.recusado"]:
                mensagem_exclusao = {
                    "id_pedido": id_pedido,
                    "produtos": self.pedidos[id_pedido]["produtos"],
                }
                self.publicar_evento(mensagem_exclusao, "pedido.excluido", ch)

        msg = {"evento": chave, "status": status}
        if chave == "pagamento.cobranca_criada":
            msg["url_pagamento"] = mensagem["url_pagamento"]
        if chave == "pedido.enviado" and "nota_fiscal" in mensagem:
            msg["nota_fiscal"] = mensagem["nota_fiscal"]

        estado.notificar(id_pedido, msg)