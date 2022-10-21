import abc

from services.model.model import ConversionTaskDetail, ConversionTask, FileFormat,FileStatus
from typing import List

class TaskRepository(abc.ABC):
    
    @abc.abstractmethod
    def register_conversion_task(self, conversion_task: ConversionTask)-> str:
        ...

    @abc.abstractmethod
    def get_conversion_task_by_id(self, task_id: str)-> ConversionTaskDetail: 
        ...

    @abc.abstractmethod
    def get_conversion_tasks_by_user_id(self, user_id: str)-> List[ConversionTaskDetail]:
        ...

    @abc.abstractmethod
    def change_target_file_format(self, task_id: str, targe_file_format: FileFormat )-> ConversionTaskDetail: 
        ...
    
    @abc.abstractmethod
    def delete_task_conversion_by_id(self, task_id: str)-> None: 
        ...
    
    @abc.abstractmethod
    def update_conversion_task(self, task_id: str,target_file_path: str, state : FileStatus ) -> None: 
        ...