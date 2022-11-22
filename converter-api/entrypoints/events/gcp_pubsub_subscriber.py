from time import sleep
from json import loads
from services.model.model import ConversionTaskDetail, FileStatus, FileFormat
from repositorios import  task_repository
from google.api_core import retry

from services import  task_service,logs
import os
_LOGGER = logs.get_logger()
from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1


def _process_file_conversion(conversion_task_detail: ConversionTaskDetail)->None:
    task_service.convert_file_task(task_repository=task_repository.TaskRepository(), 
                      conversion_task_detail=conversion_task_detail)


def start_consumer2() -> None:
    
        
        gcp_project_id = "proyecto-desarrollo-nube"
        
        while True:
            
            try:
                
                subscriber = pubsub_v1.SubscriberClient()
        
                subscription_path = subscriber.subscription_path(gcp_project_id, "audio-conversor-subscription")
            
                with subscriber:
                    # The subscriber pulls a specific number of messages. The actual
                    # number of messages pulled may be smaller than max_messages.
                    response = subscriber.pull(
                        request={"subscription": subscription_path, "max_messages": 1},
                        retry=retry.Retry(deadline=10),
                    )

                    if len(response.received_messages) > 0:
                        ack_ids = []
                        for received_message in response.received_messages:
                            _LOGGER.info("Received: [%s]",  received_message.message.data)
                            data = loads(s=received_message.message.data)
                            
                            task = ConversionTaskDetail(id = data["id"], source_file_path=data["source_file_path"], source_file_format=FileFormat[data["source_file_format"]], target_file_format=FileFormat[data["target_file_format"]], target_file_path=data["target_file_path"], state = FileStatus[data["state"]], user_mail=data["user_mail"])
                            _process_file_conversion(conversion_task_detail=task)
                            ack_ids.append(received_message.ack_id)

                        # Acknowledges the received messages so they will not be sent again.
                        subscriber.acknowledge(
                            request={"subscription": subscription_path, "ack_ids": ack_ids}
                        )

                        _LOGGER.info(
                            "Received and acknowledged [%s] messages from [%s]", len(response.received_messages),subscription_path 
                        )
                        
                    else:
                        ...
                        #_LOGGER.info(f"There are not messages from GCP subscriber")
                        print(f"There are not messages from GCP subscriber")
                    
                
            except Exception as e:
               # _LOGGER.error("Error in GCP Subscriber message",e)
               print("error", e)
   

from multiprocessing import Process

def start():
    _LOGGER.info("Starting gcp subscriber")   
    t1 = Process(target=start_consumer2)
    t1.start()
    _LOGGER.info("GCP Subscriber is running")   

    
  
    
