from services.contracts import file_conversion_scheduler
from services.model.model import ConversionTaskDetail
from json import dumps
from  services import logs 
from adapters import gcp_publisher

import os
log = logs.get_logger()
class FileGCPPubSubConversionScheduler(file_conversion_scheduler.FileConversionScheduler):


    def schedule_conversion_task(self, conversion_task: ConversionTaskDetail) -> None:
        
        log.info("Send task with id [%s] to GCP pub/sub topic [%s] message -> %s",conversion_task.id,'file.conversion.requested', conversion_task.json())
        #self._publisher.publish(self._topic_path, conversion_task.json().encode("utf-8"))
        gcp_publisher.publish_message(task = conversion_task)
        log.info(f"Task with id [%s] was sent to GCP pub/sub to convert to [%s] format", conversion_task.id, conversion_task.target_file_format)
