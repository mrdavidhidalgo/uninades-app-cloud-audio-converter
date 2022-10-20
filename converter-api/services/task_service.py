from services.contracts.task_repository import TaskRepository
from services.contracts.file_conversion_scheduler import FileConversionScheduler
from pydantic import BaseModel
from services.model.model import ConversionTask, FileFormat, ConversionTaskDetail, FileStatus

class RegisterConversionTaskInput(BaseModel):

    user_id : str
    source_file_path : str
    source_file_format: FileFormat
    target_file_format: FileFormat
    

def register_conversion_task(task_repository: TaskRepository, 
                             conversion_scheduler : FileConversionScheduler,  
                             register_conversion_task_input: RegisterConversionTaskInput)-> str:

    conversion_task = ConversionTask(user=register_conversion_task_input.user_id, 
                   source_file_path=register_conversion_task_input.source_file_path, 
                   source_file_format=register_conversion_task_input.source_file_format,
                   target_file_format= register_conversion_task_input.target_file_format)

    task_id = task_repository.register_conversion_task(conversion_task=conversion_task)
    task_detail = ConversionTaskDetail(id =task_id, 
                                source_file_format=conversion_task.source_file_format, 
                                source_file_path=conversion_task.source_file_path, 
                                target_file_format=conversion_task.target_file_format,
                                state = FileStatus.UPLOADED)
    
    

    conversion_scheduler.schedule_conversion_task(conversion_task=task_detail)

    return task_id
