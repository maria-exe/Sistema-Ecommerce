import json
import pika
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

def conectar():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    return connection, channel

# criacao de duas exchange
# ecommercie - Direct
def exchange_ecommercie(channel):
    channel.exchange_declare(exchange='eCommerce', exchange_type='direct')

# promocoes - Topics
def exchange_promocoes(channel):
    channel.exchange_declare(exchange='promocoes', exchange_type='topic')

# declara fila e binding
def binding(channel, queue_name: str, binding_keys, tipo_exchange: str): # cada serviço tem esses parametros diferente
    channel.queue_declare(queue=queue_name, durable=True)

    for binding_key in binding_keys:
        channel.queue_bind(
            exchange=tipo_exchange, 
            queue=queue_name, 
            routing_key=binding_key)

# funcoes genericas para publicar e consumir eventos
def publicar(channel, publisher, caminho, tipo_exchange: str, routing_key, mensagem):
    body = json.dumps(mensagem, sort_keys=True).encode("utf-8")

    key = RSA.import_key(open(caminho, 'rb').read())
    hash_dados = SHA256.new(body)
    assinatura = pkcs1_15.new(key).sign(hash_dados)

    properties = pika.BasicProperties(
        headers={'publisher': publisher, 'signature': assinatura},
        delivery_mode=pika.DeliveryMode.Persistent
    )
    channel.basic_publish(
        exchange=tipo_exchange, 
        routing_key=routing_key, 
        body=body,
        properties=properties
    )

def consumir(channel, queue_name: str, callback, caminho_publico):
    def _callback(ch, method, properties, body):
        headers = properties.headers or {}
        publisher = headers.get('publisher')
        assinatura = headers.get('signature')

        if publisher is None or assinatura is None:
            print("\nMensagem sem assinatura.")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        try: 
            caminho_key = f"{caminho_publico}/public_key_{publisher}.der"
            key = RSA.import_key(open(caminho_key, 'rb').read())

            # verifica assinatura
            hash_dados = SHA256.new(body)
            pkcs1_15.new(key).verify(hash_dados, assinatura)

            conteudo = json.loads(body.decode("utf-8"))
            callback(ch, method.routing_key, conteudo)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except (ValueError, TypeError, OSError, FileNotFoundError):
            print(f"Assinatura de {publisher} invalida.")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=queue_name, 
        on_message_callback=_callback, 
        auto_ack=False)

    channel.start_consuming()