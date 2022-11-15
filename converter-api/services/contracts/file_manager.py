import abc

class FileManager(abc.ABC):
    
    @abc.abstractmethod
    def get_file(self, path: str, destination_file: str)-> None:
        ...
        
    def save_file(self, path: str, file_name: str, file: bytes)-> None:
        ...