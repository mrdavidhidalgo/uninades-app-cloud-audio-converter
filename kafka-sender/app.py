from time import sleep
from json import dumps
from kafka import KafkaProducer,KafkaConsumer
from json import loads

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.info("Iniciando")
sleep(20)
producer = KafkaProducer(bootstrap_servers=['kafka:9092'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'),
                         key_serializer=lambda x: 
                         dumps(x).encode('utf-8')
                         )

for e in range(1000):
    data = {'number' : e}
    producer.send('numtest', value=data,key=e)
    log.info(data)
    sleep(5)