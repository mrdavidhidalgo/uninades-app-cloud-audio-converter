from services.contracts.task_repository import TaskRepository
from services.contracts.file_conversion_scheduler import FileConversionScheduler
from pydantic import BaseModel
from services.model.model import ConversionTask, FileFormat, ConversionTaskDetail, FileStatus
from services import  logs

_LOGGER = logs.get_logger()
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





def convert_file_task(task_repository: TaskRepository, 
                      conversion_task_detail : ConversionTaskDetail)-> None:
    
    _LOGGER.info("Se acaba de recibir el mensaje [%r] para ser procesado",conversion_task_detail)

    # conversion
    task_repository.update_conversion_task(task_id=conversion_task_detail.id,
                                           target_file_path="nuevo path", state=FileStatus.PROCESSED)
    
    # enviar email