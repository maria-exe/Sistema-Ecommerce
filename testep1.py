# processo 1 para testar comunicação
import pika, sys

# conecta com o RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel() 

channel.exchange_declare(exchange='direct_logs', exchange_type='direct')


severity = sys.argv[1] if len(sys.argv) > 1 else 'info'
message = ' '.join(sys.argv[1:]) or "info: Hello World!"
channel.basic_publish(exchange='direct_logs',
                      routing_key=severity,
                      body=message)

print(f" [x] Sent {severity}")
connection.close()