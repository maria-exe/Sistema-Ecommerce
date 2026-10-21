import random, time, threading
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

        self.caminho_publico = os.path.join(dir_atual, "public_keys")
        self.caminho_privado = os.path.join(dir_atual, "private_keys", "private_key.der")

    def get_produtos(self): # pega os produtos
        url = "http://localhost:8080/estoque"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json().get("produtos", [])
        except Exception as e:
            print(f"Erro ao acessar estoque: {e}")
        return []
    
    def consumir_evento(self):
        binding_keys = ["interesse.promocao", "interesse.cancelado"] # routing para cancelar interesse
        rabbit.binding(self.channel, self.queue_name, binding_keys, "eCommerce")
        rabbit.consumir(self.channel, self.queue_name, self.callback, self.caminho_publico)

    def gera_promocoes(self, email, categorias):
        candidatos = [produto for produto in self.get_produtos()
                    if produto["categoria"].lower() in categorias and produto["quantidade"] > 0]
        
        if not candidatos:
            return

        livro = random.choice(candidatos)
        desconto = random.randint(20, 80)
        self.envia_email(email, livro["titulo"], desconto, livro["categoria"])


    def callback(self, ch, chave, dados):
        email = dados["email"]
        categorias = dados.get("categorias") 

        if chave == "interesse.promocao":
            for categoria in categorias:
                bd.registra(email, categoria)

        elif chave == "interesse.cancelado":
            if categorias:
                for categoria in categorias:
                    bd.apaga_registro(email, categoria)
            else:
                bd.apaga_registro(email, None)  

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

    def envio_periodico(self, intervalo_segundos=30):
        while True:
            time.sleep(intervalo_segundos)
            try:
                por_email = {}
                for email, categoria in bd.interesses(): # emails e interesses do bd  
                    por_email.setdefault(email, []).append(categoria)

                for email, categorias in por_email.items():
                    self.gera_promocoes(email, categorias) # envio de emails
                    time.sleep(0.5)                           
            except Exception as e:
                return

def main(): 
    promocoes = Promocoes()
    
    thread_loop = threading.Thread(
        target=promocoes.envio_periodico, 
        args=(60,), 
        daemon=True
    )

    thread_loop.start()
    promocoes.consumir_evento()

if __name__ == "__main__":
    main()