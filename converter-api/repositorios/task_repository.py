from services.contracts import task_repository
from services.model.model import ConversionTaskDetail, FileFormat, FileStatus, ConversionTask
from repositorios.db_model import db_model
from typing import List 

class TaskRepository(task_repository.TaskRepository):

    def get_conversion_tasks_by_user_id(self, user_id: str) -> List[ConversionTaskDetail]:

        return ConversionTaskDetail(id = "1", 
                                    source_file_path="/pepe.txt", 
                                    source_file_format=FileFormat.MP3, 
                                    target_file_format=FileFormat.WAV, 
                                    state = FileStatus.UPLOADED)

    def register_conversion_task(self, conversion_task: ConversionTask) -> str:
        
        return "1234"

    def get_conversion_task_by_id(self, task_id: str) -> ConversionTaskDetail:
        return ConversionTaskDetail(id = task_id, 
                                    source_file_path="/pepe2.txt", 
                                    source_file_format=FileFormat.MP3, 
                                    target_file_format=FileFormat.WAV, 
                                    state = FileStatus.PROCESSED)

    def change_target_file_format(self, task_id: str, target_file_format: FileFormat ) -> ConversionTaskDetail:
        return ConversionTaskDetail(id = task_id, 
                                    source_file_path="/pepe3.txt", 
                                    source_file_format=FileFormat.MP3, 
                                    target_file_format=target_file_format, 
                                    state = FileStatus.UPLOADED)

    def delete_task_conversion_by_id(self, task_id: str)-> None:
        ...


