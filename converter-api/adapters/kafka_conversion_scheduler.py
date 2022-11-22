from services.contracts import file_conversion_scheduler
from services.model.model import ConversionTaskDetail
from kafka import KafkaProducer
from  services import logs 
import os
log = logs.get_logger()
class FileKafkaConversionScheduler(file_conversion_scheduler.FileConversionScheduler):


    def __init__(self):
        bootstrap_servers = os.getenv("bootstrap_servers","kafka:9092")
        sasl_plain_username= os.getenv("sasl_plain_username","user")#se debe colocar el user
        sasl_plain_password=os.getenv("sasl_plain_password","kTm5cVvQ4reC")#se debe especificar contraseña
        security_protocol=os.getenv("security_protocol","SASL_PLAINTEXT")
        sasl_mechanism=os.getenv("sasl_mechanism","PLAIN")
        
        
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                         sasl_plain_username=sasl_plain_username, sasl_plain_password=sasl_plain_password,
                         security_protocol=security_protocol, sasl_mechanism=sasl_mechanism,
                         value_serializer=lambda x: 
                         x.json().encode('utf-8'),
                         )
        
        
    def schedule_conversion_task(self, conversion_task: ConversionTaskDetail) -> None:
        
        log.info("Send task with id [%s] to Kafka topic [%s] message -> %s",conversion_task.id,'file.conversion.requested', conversion_task.json())
        self.producer.send('file.conversion.requested', value=conversion_task)
        log.info(f"Task with id [%s] was sent to Kafka to convert to [%s] format", conversion_task.id, conversion_task.target_file_format)




 

