from time import sleep
from json import dumps
from kafka import KafkaProducer,KafkaConsumer
from json import loads
import logging
log = logging.getLogger(__name__)

print("Iniciando")
sleep(3)

try:
    consumer = KafkaConsumer(
        'numtest',
        bootstrap_servers=['kafka:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        client_id='docker-client',
        group_id='my-group',
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    log.info("Hello, world")
    
    while True:
        for message in consumer:
            message = message.value
            log.info(f"Message {message}")
        sleep(5) 
        log.info("sleep")   
        
    log.info("End")

except Exception as e:
    print("Error")
    print(e)