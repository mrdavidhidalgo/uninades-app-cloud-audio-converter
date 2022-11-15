
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
        
        self._save_local(path=path, file = file)
        self._save_gcp_bucket(source_path=path, file_name = file_name)
        
    def get_file(self, path: str, file: bytes) -> None:
        return super().get_file(path, file)
        
    def _save_local(self, path: str, file:bytes)->None:
        
        binary_file = open(path, "wb")
        binary_file.write(file)
        binary_file.close()
        
    def _save_gcp_bucket(self, source_path: str, file_name: str) -> None:
        
        print(
        # f"{destination_blob_name} with contents {contents} uploaded to {bucket_name}."
            _LOGGER.info(f"{file_name} with contents {source_path} uploaded to {self._bucket_path}.")
        )
        
        storage_client = storage.Client()
        bucket = storage_client.bucket(self._bucket_path)
        blob = bucket.blob(file_name)

        blob.upload_from_string(source_path)

        
        
        