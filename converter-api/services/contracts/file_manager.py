import abc

class FileManager(abc.ABC):
    
    @abc.abstractmethod
    def get_file(self, path: str, file: bytes)-> None:
        ...
        
    def save_file(self, path: str, file_name: str, file: bytes)-> None:
        ...