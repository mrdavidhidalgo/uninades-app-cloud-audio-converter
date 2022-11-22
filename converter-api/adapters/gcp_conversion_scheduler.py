from services.contracts import file_conversion_scheduler
from services.model.model import ConversionTaskDetail
from json import dumps
from  services import logs 

from google.cloud import pubsub_v1

import os
log = logs.get_logger()
class FileGCPPubSubConversionScheduler(file_conversion_scheduler.FileConversionScheduler):


    def __init__(self):
        
        self._publisher = pubsub_v1.PublisherClient()
        
        gcp_project_id = os.getenv("gcp_project_id")
        
        if gcp_project_id is None:
            raise Exception("gcp_project_id as environment variable must be configured")
        
        self._topic_path = self._publisher.topic_path(gcp_project_id, "file.conversion.requested")
        
    def schedule_conversion_task(self, conversion_task: ConversionTaskDetail) -> None:
        
        log.info("Send task with id [%s] to GCP pub/sub topic [%s] message -> %s",conversion_task.id,'file.conversion.requested', conversion_task.json())
        self._publisher.publish(self._topic_path, conversion_task)
        log.info(f"Task with id [%s] was sent to GCP pub/sub to convert to [%s] format", conversion_task.id, conversion_task.target_file_format)




 

