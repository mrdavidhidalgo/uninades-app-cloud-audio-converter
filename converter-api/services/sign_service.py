from services.model.model import User
from services.contracts.user_repository import UserRepository
from services import exceptions
from pydantic import BaseModel


class RegisterUserInput(BaseModel):

    username : str
    mail : str
    password : str

def create_user(user_repository: UserRepository, register_user_input: RegisterUserInput):

    user_to_create = User(username = register_user_input.username, mail = register_user_input.mail, password = register_user_input.password)

    user = user_repository.get_user_by_username(username = register_user_input.username)

    if user is not None:
        raise exceptions.UserAlreadyExistError(username=register_user_input.username)
    
    return user_repository.create_user(user_to_create)

def log_in(user_repository: UserRepository, username: str, password: str)-> str:
    user = user_repository.get_user_by_username(username = username)
    
    if user is None or user.password != password:
        raise exceptions.UserOrPasswordInvalidError(username=username)
    
    return user.id