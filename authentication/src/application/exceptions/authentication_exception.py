from src.application.shared.application_exception import ApplicationException


class AuthenticationRequired(ApplicationException) : 
    code: str = "AUTHENTICATION_REQUIRED"

    def __init__(self, message: str, status=401):
        super().__init__(message, status)


