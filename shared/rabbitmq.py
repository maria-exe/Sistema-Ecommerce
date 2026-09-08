import json
import pika

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
def publicar(channel, tipo_exchange: str, routing_key, mensagem):
    channel.basic_publish(
        exchange=tipo_exchange, 
        routing_key=routing_key, 
        body=json.dumps(mensagem),
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent  
        )
    )

def consumir(channel, queue_name: str, callback):
    def _callback(ch, method, properties, body):
        payload = json.loads(body)
        callback(ch, payload)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=queue_name, 
        on_message_callback=_callback, 
        auto_ack=False)

    channel.start_consuming()