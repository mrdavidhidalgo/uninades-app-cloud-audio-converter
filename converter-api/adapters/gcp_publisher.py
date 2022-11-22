
import logging
import os
import sys
from services.model.model import ConversionTaskDetail
from  services import logs 
from google.cloud import pubsub_v1
from typing import Any, Optional

format = (
    "%(asctime)s | %(levelname)-7s | %(module)s.%(funcName)s:%(lineno)d | %(message)s"
)
publisher: Optional[pubsub_v1.PublisherClient] = None
topic_path : Optional[Any] = None

log = logs.get_logger()


def publish_message(task : ConversionTaskDetail)->None:
    
    log.info("publishing message")
    global publisher
    global topic_path
    if not publisher:
        
        gcp_project_id = os.getenv("GCP_PROJECT_ID")
        log.info("GCP_PROJECT_ID")
        
        if gcp_project_id is None:
            raise Exception("gcp_project_id as environment variable must be configured")
        
        publisher = pubsub_v1.PublisherClient()
        log.info("Client publisher created")
        
        topic_path = publisher.topic_path(gcp_project_id, "file.conversion.requested")
        
        log.info("Topic path created")
       
    
    log.info("Message ready to send")
    publisher.publish(topic_path, task.json().encode("utf-8"))
    log.info("Message sent")
    
