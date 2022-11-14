from genericpath import isfile
from repositorios.user_repository import UserRepository
from services.contracts.task_repository import TaskRepository
from services.contracts.file_conversion_scheduler import FileConversionScheduler
from pydantic import BaseModel
from services.model.model import ConversionTask, FileDetail, FileFormat, ConversionTaskDetail, FileStatus
from services import  logs
import os
import time
import smtplib
import ssl
from typing import List, Optional
import os
from google.cloud import storage

CONVERTED_FILE_PATH: str = "/converted"

class ConverterException(Exception):
    def __init__(self, *args: object, message: str) -> None:
        super().__init__(message, *args)
        self.message = message
        
class ConversionTaskDoesNotExistException(ConverterException):
    def __init__(self, *args: object, task_id: str, user_id: str) -> None:
        self.message = f"Task with id {task_id} for user {user_id} does not exist"
        super().__init__(message = self.message, *args)
        
class FileDoesNotExistException(ConverterException):
    def __init__(self, *args: object, file_name:str, user_id: str) -> None:
        self.message = f"The filename {file_name} for user {user_id} does not exist"
        super().__init__(message = self.message, *args)
        
class ConversionTaskAlreadyHasSpecificFormatException(ConverterException):
    def __init__(self, *args: object, task_id: str) -> None:
        self.message = f"Task with id {task_id} already is with current format"
        super().__init__(message = self.message, *args)
        
class ConversionTaskStatusCannotBeUpdatedException(ConverterException):
    def __init__(self, *args: object, task_id: str) -> None:
        self.message = f"Task with id {task_id} already has the file with status UPLOADED"
        super().__init__(message = self.message, *args)
        
class FileToConvertWithCurrentFormatException(ConverterException):
    def __init__(self, *args: object, file_format: FileFormat) -> None:
        self.message = f"File to convert already has {file_format} format"
        super().__init__(message = self.message, *args)
        
class SourceFileDoesNotExistException(ConverterException):
    def __init__(self, *args: object, file_name: str) -> None:
        self.message = f"File with name {file_name} does not exist"
        super().__init__(*args, message=self.message)
        

_LOGGER = logs.get_logger()
class RegisterConversionTaskInput(BaseModel):

    user_id : str
    source_file_path : str
    source_file_format: FileFormat
    target_file_format: FileFormat
    

def register_conversion_task(task_repository: TaskRepository, 
                             user_repository: UserRepository,
                             conversion_scheduler : FileConversionScheduler,  
                             register_conversion_task_input: RegisterConversionTaskInput)-> str:
    
    #TODO Validate if file exist

    conversion_task = ConversionTask(user=register_conversion_task_input.user_id, 
                   source_file_path=register_conversion_task_input.source_file_path, 
                   source_file_format=register_conversion_task_input.source_file_format,
                   target_file_format= register_conversion_task_input.target_file_format)
    
    user = user_repository.get_user_by_id(id = register_conversion_task_input.user_id)
    
    task_id = task_repository.register_conversion_task(conversion_task=conversion_task)
    task_detail = ConversionTaskDetail(id =task_id, 
                                source_file_format=conversion_task.source_file_format, 
                                source_file_path=conversion_task.source_file_path, 
                                target_file_format=conversion_task.target_file_format,
                                state = FileStatus.UPLOADED,
                                user_mail=user.mail)
    
    

    conversion_scheduler.schedule_conversion_task(conversion_task=task_detail)

    return task_id

def get_tasks_by_user_id(task_repository: TaskRepository, user_id: str)->List[ConversionTaskDetail]:
    return task_repository.get_conversion_tasks_by_user_id(user_id = user_id)

def get_task_by_id(task_repository: TaskRepository, user_id: str, task_id: int)->Optional[ConversionTaskDetail]:
    return task_repository.get_conversion_task_by_id(user_id = user_id, task_id=task_id)

def delete_file(file_name: str, file_path: str)->None:
    if not os.path.exists(file_path):
        _LOGGER.info("Path does not exist %s", file_path)
        raise SourceFileDoesNotExistException(file_name=file_name)
    
    _LOGGER.info("Deleting file with path %s", file_path)
    
    if os.path.isfile(file_path):
        os.remove(file_path)

def delete_converted_file_from_disk(file_name: str)->None:
    
    data_path : str = os.environ.get('DATA_PATH')
    
    file_path = "{}/{}/{}".format(data_path,CONVERTED_FILE_PATH,file_name)
    
    _LOGGER.info("Deleting converted file with path %s", file_path)
    
    delete_file(file_name=file_name, file_path=file_path)
    
    
def delete_source_file_from_disk(file_name: str)->None:
    
    data_path = os.environ.get('DATA_PATH')
    
    file_path = data_path+"/"+file_name
    
    _LOGGER.info("Deleting source file with path %s", file_path)
    
    delete_file(file_name=file_name, file_path=file_path)
    

def update_target_format_to_conversion_task(task_repository: TaskRepository,conversion_scheduler : FileConversionScheduler, user_id: str, task_id: int, file_format : FileFormat )->ConversionTaskDetail:
    current_conversion = get_task_by_id(task_repository= task_repository, user_id = user_id, task_id=task_id)
    
    if current_conversion is None:
        raise ConversionTaskDoesNotExistException(task_id=task_id, user_id=user_id)
    
    if current_conversion.target_file_format is file_format:
        raise ConversionTaskAlreadyHasSpecificFormatException(task_id=task_id)
    
    if current_conversion.state is FileStatus.UPLOADED:
        raise ConversionTaskStatusCannotBeUpdatedException(task_id=task_id)
    
    if current_conversion.source_file_format is file_format:
        raise FileToConvertWithCurrentFormatException(file_format=file_format)
    
    delete_converted_file_from_disk(file_name = current_conversion.target_file_path)
    
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
    
    delete_converted_file_from_disk(file_name=conversion_task.target_file_path)
    delete_source_file_from_disk(file_name=conversion_task.source_file_path)
    
    task_repository.delete_conversion_task_by_id(task_id=task_id)

    

def convert_file_task(task_repository: TaskRepository, 
                      conversion_task_detail : ConversionTaskDetail)-> None:
    

    _LOGGER.info("File conversion task is requested [%r] to be processed",conversion_task_detail)

    data_path = os.environ.get('DATA_PATH')
    email_enable = os.environ.get('EMAIL_ENABLE') == 'True'
     #cambio
    bucket_path = os.environ.get('BUCKET_PATH')
    
    # conversion
    a=conversion_task_detail
    try:
        now =  time.time()
        #cambio
        #b=convert_file(a.source_file_path,a.source_file_path, a.source_file_format,a.target_file_format,                             data_path,data_path + "/converted",conversion_task_detail.user_mail,email_enable)
        b=convert_file(a.source_file_path,a.source_file_path, a.source_file_format,a.target_file_format,                             data_path,data_path + "/converted",conversion_task_detail.user_mail,email_enable, bucket_path)

        if(b):
            now2 = time.time()
            task_time = int((now2*1000) - (now*1000))
            task_repository.update_conversion_task(task_id=conversion_task_detail.id,
                                            target_file_path=b, state=FileStatus.PROCESSED, task_duration = task_time)
            _LOGGER.info("File converted in " + str(task_time) + " miliseconds")
    except Exception as e:
        _LOGGER.error(e)
        _LOGGER.error("Error at %s",e)
        
def get_file_dir_by_name(task_repository: TaskRepository, file_name: str, user_id : str)->str:
    
    file_detail = task_repository.get_file_path_by_user_and_file_name(file_name=file_name, user_id=user_id)
    
    if file_detail is None:
        raise FileDoesNotExistException(file_name=file_name, user_id=user_id)
    
    data_path : str = os.environ.get('DATA_PATH')
    
    return "{}/{}".format(data_path,CONVERTED_FILE_PATH) if file_detail.is_converted else "{}".format(data_path)

#def convert_file (origen2, destino2, formato1, formato2, ruta1, ruta2,email, use_email):
def convert_file (origen2, destino2, formato1, formato2, ruta1, ruta2,email, use_email, ruta_deposito):
    aux = origen2.split(".")
    origen = aux[0]
    destino = origen
    _LOGGER.info("origen=%s, destino=%s, formato1=%s, formato2=%s, ruta1=%s, ruta2=%s,email=%s",origen, destino, formato1, formato2, ruta1, ruta2,email)
    comando = "/usr/bin/sox "
    #cambio
    comando2 = "/usr/bin/gsutil cp "
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
        formato_entrada=".wav" #cambio
        if(salida == "MP3"):
            parametros=" -t wav -r 8000 -c 1 " + ruta1 +"/" + origen + ".wav -t mp3 " + ruta2 +"/"  + destino + ".mp3"
        if(salida == "OGG"):
            parametros=ruta1 + "/" + origen + ".wav -r 22050 " + ruta2 +"/" + destino + ".ogg"

    if (entrada == "MP3"):
        formato_entrada=".mp3" #cambio
        if(salida == "WAV"):
            parametros=ruta1 + "/" + origen + ".mp3 -r 8000 -c1 " + ruta2 +"/" + destino + ".wav"
        if(salida == "OGG"):
            parametros=ruta1 + "/" + origen + ".mp3 " + ruta2 +"/" + destino + ".ogg"

    if (entrada == "OGG"):
        formato_entrada=".ogg" #cambio
        if(salida == "WAV"):
            parametros=ruta1 + "/" + origen + ".ogg " + ruta2 +"/" + destino + ".wav"
        if(salida == "MP3"):
            parametros=ruta1 + "/" + origen + ".ogg " + ruta2 +"/" + destino + ".mp3"

    #cambio
    if(salida == "MP3"):
        formato_salida=".mp3"
    if(salida == "WAV"):
        formato_salida=".wav"
    if(salida == "OGG"):
        formato_salida=".ogg"

    parametros2=  ruta2 +"/" + destino + formato_salida +" gs://" +  ruta_deposito + "/converted/";

    if(len(parametros) > 0):
        _LOGGER.info("Executing " + comando + " " + parametros)
        os.system(comando + parametros)
        #para copiar al repos
       #os.system(comando2 + parametros2)
        upload_file_bucket(ruta_deposito, ruta2 +"/" + destino + formato_salida , "/converted/" + destino + formato_salida)
        if use_email:
           if(len(email) > 2):
               _LOGGER.info("Sending confirmation to %s", email)
               send_mail(email, destino + "." + salida2)
        return destino + "." + salida2
    else:
        _LOGGER.info("Formats not supported " + entrada + " to " + salida)
        return False


#cambio
def upload_file_bucket(bucket_name, contents, destination_file):

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_file)

    blob.upload_from_string(contents)

    print(
       # f"{destination_blob_name} with contents {contents} uploaded to {bucket_name}."
        _LOGGER.info("{destination_file} with contents {contents} uploaded to {bucket_name}.")
    )



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
