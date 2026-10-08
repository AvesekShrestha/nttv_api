from src.application.shared.application_exception import ApplicationException


class UserAlreadyExists(ApplicationException) : 
    code: str = "USER_ALREADY_EXISTS"

    def __init__(self, message: str, status=409):
        super().__init__(message, status)

class UserNotFound(ApplicationException) : 
    code: str = "USER_NOT_FOUND"

    def __init__(self, message: str, status=404):
        super().__init__(message, status)

class InactiveUser(ApplicationException):
    code: str = "INACTIVE_USER"

    def __init__(self, message: str, status=403):
        super().__init__(message, status)
