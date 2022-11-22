from time import sleep
from json import loads

from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1


#def _process_file_conversion(conversion_task_detail: ConversionTaskDetail)->None:
    
    #task_service.convert_file_task(task_repository=task_repository.TaskRepository(), 
    #                  conversion_task_detail=conversion_task_detail)


def callback(message: pubsub_v1.subscriber.message.Message) -> None:
        print(f"Received {message}.")
        print(f"Received task {message.data}.")
        #_process_file_conversion(conversion_task_detail=message.data)
        message.ack()

def start_consumer()->None:
    
    
    try:
        
        subscriber = pubsub_v1.SubscriberClient()
        
        subscriber = pubsub_v1.SubscriberClient()
        
        subscription_path = subscriber.subscription_path("projectId", "audio-conversor-subscription")
        
        streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
        
        print(f"Listening for messages on {subscription_path}..\n")
        
        with subscriber:
            try:
                # When `timeout` is not set, result() will block indefinitely,
                # unless an exception is encountered first.
                streaming_pull_future.result(timeout=None)
            except TimeoutError:
                streaming_pull_future.cancel()  # Trigger the shutdown.
                streaming_pull_future.result()  # Block until the shutdown is complete.
        
    except Exception as e:
        print(f"error {e}")
        ...
    
    
start_consumer()
  
    
