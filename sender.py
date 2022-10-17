from time import sleep
from json import dumps
from kafka import KafkaProducer,KafkaConsumer
from json import loads


producer = KafkaProducer(bootstrap_servers=['kafka:9092'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'),
                         key_serializer=lambda x: 
                         dumps(x).encode('utf-8')
                         )

for e in range(100):
    data = {'numberaa' : e}
    producer.send('numtest', value=data,key=e)
    print(data)
    sleep(5)