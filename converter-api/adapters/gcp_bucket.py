
from services.contracts import file_manager
from services.task_service import BadConfigurationForFileStorageException
import os
from google.cloud import storage
from services import  logs


_LOGGER = logs.get_logger()

class GCPBucket(file_manager.FileManager):
    
    def __init__(self) -> None:
        self._bucket_path = os.environ.get('BUCKET_PATH')
        if self._bucket_path is None:
            raise BadConfigurationForFileStorageException(message='BUCKET_PATH must be configured')
        super().__init__()
    
    def save_file(self, path: str, file_name: str, file: bytes) -> str:
        
        
        # f"{destination_blob_name} with contents {contents} uploaded to {bucket_name}."
        _LOGGER.info(f"{file_name} uploaded to {self._bucket_path}.")
        
        _LOGGER.info("Bucket starting")
        storage_client = storage.Client()
        _LOGGER.info("client storaged and before bucket")
        bucket = storage_client.bucket(self._bucket_path)
        _LOGGER.info("after bucket")
        blob = bucket.blob(file_name)
        _LOGGER.info("After blob")

        blob.upload_from_string(content_type="application/octet-stream", data= file)
        _LOGGER.info("Bucket file uploaded finish")
        
    def get_file(self, path: str, destination_file : str) -> None:
        storage_client = storage.Client()

        bucket = storage_client.bucket(self._bucket_path)
        file = bucket.blob(path)
        file.download_to_filename(destination_file)

        print(
            "Downloaded storage object {} from bucket {} to local file {}.".format(
                path, self._bucket_path, destination_file
            )
        )
          

        
        
        