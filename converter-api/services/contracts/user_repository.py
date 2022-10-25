import abc
from services.model.model import User
from typing import Optional

class UserRepository(abc.ABC):
    @abc.abstractmethod
    def create_user(self, user: User):
        ...

    @abc.abstractmethod
    def get_user_by_username(self, username: str)-> Optional[User]:
        ...
    
    @abc.abstractmethod    
    def get_user_by_mail(self, username: str)-> Optional[User]:
        ...
    
    @abc.abstractmethod
    def get_user_by_id(self, id: str)-> Optional[User]:
        ...

    