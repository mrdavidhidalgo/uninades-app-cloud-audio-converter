from services.contracts.task_repository import TaskRepository
from services.contracts.file_conversion_scheduler import FileConversionScheduler
from pydantic import BaseModel
from services.model.model import ConversionTask, FileFormat, ConversionTaskDetail, FileStatus
from services import  logs
import os
import time
import smtplib
import ssl
from typing import List, Optional
import os

class ConverterException(Exception):
    def __init__(self, *args: object, message: str) -> None:
        super().__init__(message, *args)
        self.message = message

_LOGGER = logs.get_logger()
class RegisterConversionTaskInput(BaseModel):

    user_id : str
    source_file_path : str
    source_file_format: FileFormat
    target_file_format: FileFormat
    

def register_conversion_task(task_repository: TaskRepository, 
                             conversion_scheduler : FileConversionScheduler,  
                             register_conversion_task_input: RegisterConversionTaskInput)-> str:
    
    #TODO Validate if file exist

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

def get_tasks_by_user_id(task_repository: TaskRepository, user_id: str)->List[ConversionTaskDetail]:
    return task_repository.get_conversion_tasks_by_user_id(user_id = user_id)

def get_task_by_id(task_repository: TaskRepository, user_id: str, task_id: int)->Optional[ConversionTaskDetail]:
    return task_repository.get_conversion_task_by_id(user_id = user_id, task_id=task_id)

def update_target_format_to_conversion_task(task_repository: TaskRepository,conversion_scheduler : FileConversionScheduler, user_id: str, task_id: int, file_format : FileFormat )->ConversionTaskDetail:
    current_conversion = get_task_by_id(task_repository= task_repository, user_id = user_id, task_id=task_id)
    
    if current_conversion is None:
        raise ConverterException(message=f"Task with id {task_id} for user {user_id} does not exist")
    
    if current_conversion.target_file_format is file_format:
        raise ConverterException(message=f"Task with id {task_id} already is with current format")
    
    if current_conversion.state is FileStatus.UPLOADED:
        raise ConverterException(message=f"Task with id {task_id} already has the file with status UPLOADED")
    
    if current_conversion.source_file_format is file_format:
        raise ConverterException(message=f"File to convert already has this format")
    
    #TODO Delete old file
    #if os.path.isfile(current_conversion.targ):
    #    os.remove(file_path)
    #    print("File has been deleted")
    # Update task
    task_repository.update_target_format_to_task(task_id=task_id, state = FileStatus.UPLOADED, new_file_format=file_format)
    
    conversion_task = ConversionTaskDetail(id = task_id, 
                                           source_file_path=current_conversion.source_file_path, 
                                           source_file_format=current_conversion.source_file_format, 
                                           target_file_format=file_format, 
                                           state = FileStatus.UPLOADED)
    
    
    
    # publish message
    
    conversion_scheduler.schedule_conversion_task(conversion_task=conversion_task)
    
    return conversion_task

def delete_conversion_task(task_repository: TaskRepository, 
                      task_id : str, user_id : str)-> None:
    
    conversion_task = task_repository.get_conversion_task_by_id(task_id=task_id, user_id=user_id)
    
    if conversion_task is None:
        raise ConverterException(message=f"Task with id {task_id} for user {user_id} does not exist")
    
    if conversion_task.state is FileStatus.UPLOADED:
        raise ConverterException(message = f"Task with id {task_id} is in progress state")
    
    task_repository.delete_conversion_task_by_id(task_id=task_id)
    

def convert_file_task(task_repository: TaskRepository, 
                      conversion_task_detail : ConversionTaskDetail)-> None:
    

    _LOGGER.info("Se acaba de recibir el mensaje [%r] para ser procesado",conversion_task_detail)

    data_path = os.environ.get('DATA_PATH')
    email_enable = os.environ.get('EMAIL_ENABLE') == 'True'
    
    # conversion
    a=conversion_task_detail
    try:
        b=convert_file(a.source_file_path,a.source_file_path, a.source_file_format,a.target_file_format,
                            data_path,data_path + "/converted",'frankcandanoza@gmail.com',email_enable)
        if(b):
            task_repository.update_conversion_task(task_id=conversion_task_detail.id,
                                            target_file_path=b, state=FileStatus.PROCESSED)
    except Exception as e:
        _LOGGER.error(e)
        _LOGGER.error("Error at %s",e)
    
    # enviar email

def convert_file (origen2, destino2, formato1, formato2, ruta1, ruta2,email, use_email):
    
    aux = origen2.split(".")
    origen = aux[0]
    destino = origen
    _LOGGER.info("origen=%s, destino=%s, formato1=%s, formato2=%s, ruta1=%s, ruta2=%s,email=%s",origen, destino, formato1, formato2, ruta1, ruta2,email)
    comando = "/usr/bin/sox "
    parametros=""
    entrada= formato1.value
    salida= formato2.value
    salida2=salida.lower()
    destino = destino.split(".")[0]

    if not os.path.isdir(ruta1):
        os.system(f"mkdir -p {ruta1}")
    if not os.path.isdir(ruta2):
        os.system(f"mkdir -p {ruta2}")


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
        _LOGGER.info("Executing " + comando + " " + parametros)
        os.system(comando + parametros)
        if use_email:
           if(len(email) > 2):
               _LOGGER.info("Sending confirmation to %s", email)
               send_mail(email, destino + "." + salida2)
        return destino + "." + salida2
    else:
        _LOGGER.info("Formats not supported " + entrada + " to " + salida)
        return False

def send_mail(email, filename):
    _LOGGER.info("Sending email to %s",email)
    gmail_user = 'fileconverter2022@gmail.com'
    gmail_app_password = 'sldtehxsoxprxemj'
    sent_from = gmail_user
    sent_to = [email]
    sent_subject = "Your audio file has been converted"
    sent_body = ("Hi\n\n"
                "Audio file %s has been converted\n"
                "\n"
                "Regards\n"
                "Audio-converter-app\n", filename)

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(sent_to), sent_subject, sent_body)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        server.sendmail(sent_from, sent_to, email_text)
        server.close()

        print('Email sent!')
    except Exception as exception:
        print("Error: %s!\n\n" % exception)
