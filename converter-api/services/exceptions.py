
class ConversionApiError(Exception):
    def __init__(
        self,
        *args: object,
        username: str,
        task_id : str,
        message: str,
    ) -> None:
        super().__init__(username, message, *args)
        self.username = username
        self.message = message
        self.task_id = task_id

class UserAlreadyExistError(Exception):
    def __init__(self, *args: object, username: str) -> None:
        message = f"There is a user with username [{username}]"
        super().__init__(
            username,
            message,
            *args,
        )
        self.message = message

class UserOrPasswordInvalidError(Exception):
    def __init__(self, *args: object, username: str) -> None:
        message = f"The username or password is invalid"
        super().__init__(
            username,
            message,
            *args,
        )
        self.message = message
