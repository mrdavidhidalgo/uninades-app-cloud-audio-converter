
from services.contracts import file_manager
import os
from google.cloud import storage
from services import  logs


_LOGGER = logs.get_logger()

class LocalStorage(file_manager.FileManager):
    def save_file(self, path: str, file_name: str, file: bytes) -> str:
        
        print(
            _LOGGER.info(f"Saving {path} in local storage.")
        )
        
        binary_file = open(path, "wb")
        binary_file.write(file)
        binary_file.close()
        
    def get_file(self, path: str, file: bytes) -> None:
        return super().get_file(path, file)
        