from services.contracts.task_repository import TaskRepository
from services.contracts.file_conversion_scheduler import FileConversionScheduler
from pydantic import BaseModel
from services.model.model import ConversionTask, FileFormat, ConversionTaskDetail, FileStatus
from services import  logs
import os
import time
import smtplib
import ssl

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
    a=conversion_task_detail
    b=convertir_archivo(a.source_file_path,a.source_file_path, a.source_file_format,a.target_file_format, '/opt/data',"/opt/data/converted",'')
    if(b):
        task_repository.update_conversion_task(task_id=conversion_task_detail.id,
                                           target_file_path=b, state=FileStatus.PROCESSED)
    
    # enviar email


def convertir_archivo (origen, destino, formato1, formato2, ruta1, ruta2,email):
    comando = "/usr/bin/sox "
    parametros=""

    entrada= formato1.replace('FileFormat.', '')
    salida= formato2.replace('FileFormat.', '')
    salida2=salida.lower()

    if not os.path.isdir(ruta1):
        os.system("mkdir -p %s", ruta1)
    if not os.path.isdir(ruta2):
        os.system("mkdir -p %s", ruta2)


    if (entrada == "WAV"):
        if(salida == "MP3"):
            parametros=" -t wav -r 8000 -c 1 " + ruta1 +"/" + origen + ".wav -t mp3 " + ruta2 +"/"  + destino + ".mp3"
        if(salida == "OGG"):
            parametros=ruta1 + "/" + origen + ".wav -r 22050 " + ruta2 +"/" + destino + ".ogg"

    if (entrada == "MP3"):
        if(salida == "WAV"):
            parametros=ruta1 + "/" + origen + ".mp3 -r 8000 -c1 " + ruta2 +"/" + destino + ".wav"
        if(salida == "OGG"):
            parametros=ruta1 + "/" + origen + ".mp3 " + ruta2 +"/" + destino + ".ogg"

    if (entrada == "OGG"):
        if(salida == "WAV"):
            parametros=ruta1 + "/" + origen + ".ogg " + ruta2 +"/" + destino + ".wav"
        if(salida == "MP3"):
            parametros=ruta1 + "/" + origen + ".ogg " + ruta2 +"/" + destino + ".mp3"

    if(len(parametros) > 0):
        os.system(comando + parametros)
        print("Executing " + comando + " " + parametros)
        if(len(email) > 2):
            print("Sending confirmation to ", email)
            send_mail(email)
        return destino + "." + salida2
    else:
        print("Formats not supported " + entrada + " to " + salida)
        return False

def send_mail(email):
    pass
