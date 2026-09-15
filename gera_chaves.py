import os
from Crypto.PublicKey import RSA

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICOS = ["principal", "estoque", "pagamento", "entrega"]

def gera_chaves():
    chaves = {}

    for servico in SERVICOS:
        pasta_servico = os.path.join(BASE_DIR, servico)
        pasta_privada = os.path.join(pasta_servico, "private_keys")
        pasta_publica = os.path.join(pasta_servico, "public_keys")
        
        os.makedirs(pasta_privada, exist_ok=True)
        os.makedirs(pasta_publica, exist_ok=True)
        
        key = RSA.generate(2048)
        chaves[servico] = key.publickey().export_key(format='DER')
        
        with open(os.path.join(pasta_privada, "private_key.der"), 'wb') as f:
            f.write(key.export_key(format='DER'))
            
    distribuicao = {
        "principal": ["estoque", "pagamento", "entrega"], 
        "estoque": ["principal"],                        
        "pagamento": ["estoque"],                        
        "entrega": ["pagamento"]                          
    }
    
    for consumidor, produtores in distribuicao.items():
        pasta_publica = os.path.join(BASE_DIR, consumidor, "public_keys")
        for produtor in produtores:
            with open(os.path.join(pasta_publica, f"public_key_{produtor}.der"), 'wb') as f:
                f.write(chaves[produtor])
                
    print("\nChaves geradas!")

if __name__ == "__main__":
    gera_chaves()