from src.application.shared.application_exception import ApplicationException

class AuthorizationRequired(ApplicationException) : 
    code: str = "AUTHORIZATION_EXCEPTION"

    def __init__(self, message: str, status=403):
        super().__init__(message, status)
