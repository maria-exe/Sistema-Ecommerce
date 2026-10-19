import random
import sys, os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import shared.rabbitmq as rabbit
import bd.clientes_bd as bd

import requests
import resend

from dotenv import load_dotenv
load_dotenv()
resend.api_key = os.environ["RESEND_KEY"]

class Promocoes: 
    def __init__(self):
        self.connection, self.channel = rabbit.conectar()
        rabbit.exchange_promocoes(self.channel)
        
        dir_atual = os.path.dirname(os.path.abspath(__file__))
        
        self.servico = "promocoes"
        self.queue_name = "promocoes_queue"

        self.caminho_privado = os.path.join(dir_atual, "private_keys", "private_key.der")
        self.caminho_publico = os.path.join(dir_atual, "public_keys", "principal_public_key.der")

    def get_produtos(self): # pega os produtos
        url = "http://localhost:8080/estoque"
        produtos = requests.get(url, timeout=5)
        return produtos.json().get("produtos", [])
    
    def consumir_evento(self):
        binding_keys = ["interesse.promocao", "interesse.cancelado"] # routing para cancelar interesse
        rabbit.binding(self.channel, self.queue_name, binding_keys, "eCommerce")
        rabbit.consumir(self.channel, self.queue_name, self.callback, self.caminho_publico)

    def gera_promocoes(self, email, categoria):
        produtos = self.get_produtos()
        
        produtos_promocoes = []

        # envia promocoes de produtos da categoria de interesse
        for produto in produtos:
            if produto["categoria"] == categoria:
                produtos_promocoes.append(produto)

        if not produtos_promocoes:
            return 

        livro = random.choice(produtos_promocoes)
        desconto = random.randint(20, 80)

        self.envia_email(email, livro["titulo"], desconto, categoria)
    
    def callback(self, ch, chave, dados):
        email = dados["email"]
        categoria = dados["categoria"] 

        if chave == "interesse.promocao":
            bd.registra(email, categoria)  
            self.gera_promocoes(email, categoria)
        else:
            bd.apaga_registro(email, categoria) 

    def envia_email(self, receiver, livro, desconto, categoria):
        caminho = os.path.join(os.path.dirname(__file__), "email.html")
        with open(caminho, "r", encoding="utf-8") as f:
            html = f.read()

        html = html.replace("{livro}", str(livro))
        html = html.replace("{desconto}", str(desconto))
        
        params: resend.Emails.SendParams = {
        "from": "Página Sete <onboarding@resend.dev>",
        "to": [receiver],
        "subject": f"Promoção para livros de {categoria}!",
        "html": html,
        }

        try:
            email = resend.Emails.send(params)
            print(email)
        except Exception as error:
            print(error)

def main(): 
    promocoes = Promocoes()
    promocoes.consumir_evento()

if __name__ == "__main__":
    main()