from services.contracts import file_conversion_scheduler
from services.model.model import ConversionTaskDetail, FileFormat, FileStatus, ConversionTask
from repositorios.db_model import db_model
from typing import List 
from json import dumps
from kafka import KafkaProducer,KafkaConsumer
from  services import logs 
log = logs.get_logger()
class FileConversionScheduler(file_conversion_scheduler.FileConversionScheduler):

    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=['kafka:9092'],
                         value_serializer=lambda x: 
                         x.json().encode('utf-8'),
                         )
    def schedule_conversion_task(self, conversion_task: ConversionTaskDetail) -> None:
        
        log.info("Send task with id [%s] to Kafka topic [%s] message -> %s",conversion_task.id,'file.conversion.requested', conversion_task.json())
        self.producer.send('file.conversion.requested', value=conversion_task)
        log.info(f"Task with id [%s] was sent to Kafka to convert to [%s] format", conversion_task.id, conversion_task.target_file_format)




 

