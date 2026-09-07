# processo 2 para testar comunicação
# receber apenas um subconjuntos de mensagens
import pika, sys

# conecta com o RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

result = channel.queue_declare(queue='', exclusive=True) # o servidor escolhe uma nome aleatório para a fila

queue_name = result.method.queue

severities = sys.argv[1:]

if not severities:
    sys.stderr.write("Usage: %s [info] [warning] [error]\n" % sys.argv[0])
    sys.exit(1)


for severity in severities: 
    channel.queue_bind(exchange='direct_logs',
                       queue=queue_name,
                       routing_key=severity)

def callback(ch, method, properties, body):
    print(f"[x] {method.routing_key:{body}}")

channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True
)

channel.start_consuming()

# a mensagem vai para as filas cujas binding keys matches com o routing key da mensagem
# da para fazer binding com múltiplas filas com a mesma binding key