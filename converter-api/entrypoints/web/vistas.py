

from flask_restful import Resource
from services import sign_service, task_service
from services import exceptions
from adapters import conversion_scheduler
from repositorios import user_repository, task_repository
from flask import request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
import pydantic


class VistaHealth(Resource):

    def get(self):

        return {"msg": "Health Check"}

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
            register_user_input = sign_service.RegisterUserInput(username = request.json["username"], mail= request.json["email"], password = request.json["password1"])
            user_id = sign_service.create_user(register_user_input=register_user_input, user_repository=user_repository.UserRepository())   
            token_de_acceso = create_access_token(identity=user_id)
            return {"mensaje": "User was created succesfully", "token": token_de_acceso, "id": user_id}
        except (exceptions.UserAlreadyExistError) as e:
            return {"errors": { "type": f"/exceptions/{type(e).__name__}",
                                "detail": e.message,
                              } 
                    }, 400
        except pydantic.ValidationError as e:
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
            return {"mensaje": "User successfully logged in", "token": token_de_acceso, "id": user_id}
        except exceptions.UserOrPasswordInvalidError as e:
            return e.message, 400

class VistaTask(Resource):
    
    @jwt_required()
    def post(self):

        try:
            user_id = get_jwt_identity() 
            input_task = task_service.RegisterConversionTaskInput(user_id=user_id, 
                                                             source_file_path=request.json["fileName"], 
                                                             source_file_format=extract_file_format(request.json["fileName"]),
                                                             target_file_format=task_service.FileFormat[request.json["newFormat"]], )

            task_id = task_service.register_conversion_task(task_repository=task_repository.TaskRepository(), 
                                                            conversion_scheduler=conversion_scheduler.FileConversionScheduler(),
                                                            register_conversion_task_input=input_task)

            return {"mensaje": f"Task with id [{task_id}] was created"}
        except exceptions.UserOrPasswordInvalidError as e:
            return e.message, 400
        except pydantic.ValidationError as e:
            return {"errors": [
                    {
                        "type": "/exceptions/InvalidFormat",
                        "detail": error["msg"],
                    }
                    for error in e.errors()
                ]}, 400

def extract_file_format(filename: str)-> task_service.FileFormat:
    return task_service.FileFormat.MP3
 