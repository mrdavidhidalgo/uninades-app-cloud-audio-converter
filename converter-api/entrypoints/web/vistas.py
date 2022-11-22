

from flask_restful import Resource
from services import sign_service, task_service,logs
from services import exceptions
from adapters import gcp_bucket, kafka_conversion_scheduler, local_storage, gcp_conversion_scheduler
from repositorios import user_repository, task_repository
from flask import request, send_from_directory
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from werkzeug.utils import secure_filename
import pydantic
import os
log = logs.get_logger()

GCP_STORAGE_FILE_MANAGER = "GCP_STORAGE"

class VistaHealth(Resource):

    def get(self):

        return {"msg": "Up"}

class VistaSignUp(Resource):
    #@jwt_required()
    def post(self):

        password_1 = request.json["password1"]
        password_2 = request.json["password2"]

        if password_1 != password_2:
            return {"errors": { "type": f"/exceptions/DifferentPasswordsError",
                                "detail": "password and its confirmation must be the same",
                              } 
                    }, 400

        try:
            register_user_input = sign_service.RegisterUserInput(username = request.json["username"], mail= request.json["mail"], password = password_1)
            user_id = sign_service.create_user(register_user_input=register_user_input, user_repository=user_repository.UserRepository())   
            token_de_acceso = create_access_token(identity=user_id)
            return {"message": "User was created succesfully", "token": token_de_acceso, "id": user_id}
        except (exceptions.UserAlreadyExistError) as e:
            return {"errors": { "type": f"/exceptions/{type(e).__name__}",
                                "detail": e.message,
                              } 
                    }, 400
        except pydantic.ValidationError as e:
            print(e)
            return {"errors": [
                    {
                        "type": "/exceptions/InvalidFormat",
                        "detail": error["msg"],
                    }
                    for error in e.errors()
                ]}, 400


class VistaLogin(Resource):
    #@jwt_required()
    def post(self):

        try:

            user_id = sign_service.log_in(user_repository=user_repository.UserRepository(), username=request.json["username"], password = request.json["password"])
            token_de_acceso = create_access_token(identity=user_id)
            return {"message": "User successfully logged in", "token": token_de_acceso, "id": user_id}
        except exceptions.UserOrPasswordInvalidError as e:
            return e.message, 400
        
class VistaFiles(Resource):
    
    @jwt_required()
    def get(self, file_name: str):
        try:
            
            user_id = get_jwt_identity() 
            log.info("Getting file with name [%s] from user %s",file_name, user_id)
            
            file_manager = os.environ.get('FILE_MANAGER', GCP_STORAGE_FILE_MANAGER)
            
            file_dir = task_service.get_file_dir_by_name(task_repository=task_repository.TaskRepository(), 
                                               file_manager=gcp_bucket.GCPBucket() if file_manager == GCP_STORAGE_FILE_MANAGER else local_storage.LocalStorage(),          
                                               user_id = user_id, 
                                               file_name=file_name)
            
            return send_from_directory(file_dir,
                                       file_name)
                     
        except task_service.ConverterException as e:
            return {"error": {"type": "/exceptions/ConverterException",
                        "detail": e.message
                    
                    
            }}, 400
        except pydantic.ValidationError as e:
            log.error(e)
            return {"errors": [
                    {
                        "type": "/exceptions/InvalidFormat",
                        "detail": error["msg"],
                    }
                    for error in e.errors()
                ]}, 400

class VistaTasks(Resource):
    
    @jwt_required()
    def post(self):

        try:
            user_id = get_jwt_identity() 
            log.info("Creating task for %s",user_id)
            target_format = request.form["newFormat"]
            name = request.form["fileName"]
            file = request.files['file']
            if 'file' not in request.files or not file.filename:
                return {"error": {"type": "/exceptions/ConverterException",
                        "detail": "Debe cargar un archivo para conversión"}}
            
            #Aquí necesitamos enviarlo a disco
            """
            file.save(f"{data_path}/{name}")
            
            """
            file.stream.seek(0)
            audio = file.read()
            print(f"Tipo {type(audio)}")
            
            file_manager = os.environ.get('FILE_MANAGER', GCP_STORAGE_FILE_MANAGER)
            
            
            validate_file_format(format = target_format)
            
            input_task = task_service.RegisterConversionTaskInput(user_id=user_id, 
                                                             source_file_path=name, 
                                                             source_file_format=extract_file_format(request.form["fileName"]),
                                                             target_file_format=task_service.FileFormat[target_format], )

            task_id = task_service.register_conversion_task(task_repository=task_repository.TaskRepository(), 
                                                            user_repository=user_repository.UserRepository(),
                                                            #conversion_scheduler=kafka_conversion_scheduler.FileKafkaConversionScheduler(),
                                                            conversion_scheduler=gcp_conversion_scheduler.FileGCPPubSubConversionScheduler(),
                                                            register_conversion_task_input=input_task,
                                                            #file_manager=gcp_bucket.GCPBucket(),
                                                            file_manager=gcp_bucket.GCPBucket() if file_manager == GCP_STORAGE_FILE_MANAGER else local_storage.LocalStorage(),
                                                            file=audio, file_name= name)

            return {"message": f"Task with id [{task_id}] was created"}
        except task_service.ConverterException as e:
            return {"error": {"type": "/exceptions/ConverterException",
                        "detail": e.message
                    
                    
            }}, 400
        except pydantic.ValidationError as e:
            return {"errors": [
                    {
                        "type": "/exceptions/InvalidFormat",
                        "detail": error["msg"],
                    }
                    for error in e.errors()
                ]}, 400
           
    @jwt_required()
    def get(self):
        try:
            user_id = get_jwt_identity() 
            log.info("Getting tasks for user %s",user_id)
            
            all_data = task_service.get_tasks_by_user_id(task_repository=task_repository.TaskRepository(), 
                                                         user_id = user_id)
            return [{"id": data.id, 
                     "filename": data.source_file_path, 
                     "source_format": data.source_file_format.value, 
                     "target_file_format": data.target_file_format.value, 
                     "target_file_path": data.target_file_path,
                     "status": data.state.value } 
                for data in all_data]
            
           
        except task_service.ConverterException as e:
            return {"error": {"type": "/exceptions/ConverterException",
                        "detail": e.message
                    
                    
            }}, 400
        except pydantic.ValidationError as e:
            print(e)
            return {"errors": [
                    {
                        "type": "/exceptions/InvalidFormat",
                        "detail": error["msg"],
                    }
                    for error in e.errors()
                ]}, 400
            
            
    
            
class VistaTask(Resource):
    
    @jwt_required()
    def get(self, task_id: int):
        try:
            user_id = get_jwt_identity() 
            log.info("Getting task with id %s",task_id)
            
            data = task_service.get_task_by_id(task_repository=task_repository.TaskRepository(), 
                                               user_id = user_id, 
                                               task_id=task_id)
            
            return {"id": data.id, 
                     "filename": data.source_file_path, 
                     "source_format": data.source_file_format.value, 
                     "target_file_format": data.target_file_format.value, 
                     "status": data.state.value } if data is not None else {}
                     
        except task_service.ConverterException as e:
            return {"error": {"type": "/exceptions/ConverterException",
                        "detail": e.message
                    
                    
            }}, 400
        except pydantic.ValidationError as e:
            log.error(e)
            return {"errors": [
                    {
                        "type": "/exceptions/InvalidFormat",
                        "detail": error["msg"],
                    }
                    for error in e.errors()
                ]}, 400
            
    @jwt_required()
    def put(self, task_id: int):
        
        try: 
            user_id = get_jwt_identity() 
            log.info("updating task with id %s",task_id)
            
            target_format = request.json["newFormat"]
            validate_file_format(format = target_format)
            
            data = task_service.update_target_format_to_conversion_task(task_repository=task_repository.TaskRepository(),
                                                                        conversion_scheduler=kafka_conversion_scheduler.FileKafkaConversionScheduler(), 
                                                                        user_id = user_id, 
                                                                        task_id=task_id, 
                                                                        file_format= task_service.FileFormat[target_format] )
            
        
            return {"id": data.id, 
                        "filename": data.source_file_path, 
                        "source_format": data.source_file_format.value, 
                        "target_file_format": data.target_file_format.value, 
                        "status": data.state.value } if data is not None else {}
        
        except task_service.ConverterException as e:
            return {"error": {"type": "/exceptions/ConverterException",
                        "detail": e.message
                    
                    
            }}, 400
        except pydantic.ValidationError as e:
            return {"errors": [
                    {
                        "type": "/exceptions/InvalidFormat",
                        "detail": error["msg"],
                    }
                    for error in e.errors()
                ]}, 400
            
    @jwt_required()
    def delete(self, task_id: int):
        
        try: 
            user_id = get_jwt_identity() 
            log.info("deleting task with id %s",task_id)
            
            task_service.delete_conversion_task(task_repository=task_repository.TaskRepository(), task_id=task_id, user_id=user_id)
            
            return f"Task with id {task_id} was deleted successfully"
        
        except task_service.ConverterException as e:
            return {"error": {"type": "/exceptions/ConverterException",
                        "detail": e.message
                    
                    
            }}, 400
            

        
            
def extract_file_format(filename: str)-> task_service.FileFormat:
    extension = filename.split(".")[1].upper()
    
    validate_file_format(format = extension)
    
    return task_service.FileFormat[extension]

def validate_file_format(format : str):
    
    if not hasattr(task_service.FileFormat, format.upper()):
        raise task_service.ConverterException(message = f"Format [{format}] not available for conversion")  
 