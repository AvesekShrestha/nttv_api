from src.application.shared.application_exception import ApplicationException


class InvalidPassword(ApplicationException) : 
    code: str = "INVALID_PASSWORD"

    def __init__(self, message: str, status=401):
        super().__init__(message, status)

