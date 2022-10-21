from time import sleep
from kafka import KafkaConsumer
from json import loads
from services.model.model import ConversionTaskDetail
from services import logs
import json
from repositorios import  task_repository
from services import  task_service,logs

_LOGGER = logs.get_logger()

_LOGGER.info("Iniciando Kafka consumer")

def _send_message(conversion_task_detail: ConversionTaskDetail)->None:
    
    task_service.convert_file_task(task_repository=task_repository.TaskRepository(), 
                      conversion_task_detail=conversion_task_detail)


def start_consumer()->None:
    

    try:
        consumer = KafkaConsumer(
            'file.conversion.requested',
            bootstrap_servers=['kafka:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            client_id='docker-client',
            group_id='my-group',
            value_deserializer=lambda x: ConversionTaskDetail(**json.loads(x.decode('utf-8'))))
        
        while True:
            for message in consumer:
                
                message_to_send = message.value
                _LOGGER.info(f"Taks {message_to_send.id} was received from kafka message-> {message_to_send}")
                _send_message(message_to_send)
                
            sleep(5) 
            _LOGGER.info("sleep kafka consumer")   
        
    except Exception as e:
        _LOGGER.error("sending Kakka message %s",)
    
    
from multiprocessing import Process

def start():
    _LOGGER.info("Starting kafka consumer")   
    t1 = Process(target=start_consumer)
    t1.start()
    _LOGGER.info("Kafka consumer is running")   