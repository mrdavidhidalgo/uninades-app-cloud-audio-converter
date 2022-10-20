from services.contracts import user_repository
from services.model.model import User
from repositorios.db_model import db_model
from typing import Optional

class UserRepository(user_repository.UserRepository):
   
    def create_user(self, user: User)-> str:
                
        new_user = db_model.User(name = user.username, username = user.username, mail = user.mail, password = user.password)
        db_model.db.session.add(new_user)
        db_model.db.session.commit()

        persisted_user = db_model.User.query.filter(db_model.User.username == new_user.username).first()
        if persisted_user is not None:
            return persisted_user.id

        raise Exception("Client was not created")


    def get_user_by_username(self, username: str)-> Optional[User]:
        return db_model.User.query.filter(db_model.User.username == username).first()
