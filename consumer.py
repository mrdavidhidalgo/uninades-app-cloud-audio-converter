from time import sleep
from json import dumps
from kafka import KafkaProducer,KafkaConsumer
from json import loads

print("Iniciando")
consumer = KafkaConsumer(
    'numtest',
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     client_id='consumer',
     group_id='my-group10',
     value_deserializer=lambda x: loads(x.decode('utf-8')))
print("Iniciando")
while True:
    for message in consumer:
        message = message.value
        print(f"Message {message}")
    print("Procesando")
    sleep(5)
        
print("End")