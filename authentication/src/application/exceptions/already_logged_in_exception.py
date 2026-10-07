from src.application.shared.application_exception import ApplicationException

class AlreadyLoggedIn(ApplicationException) : 
    code: str = "ALREADY_LOGGED_IN"

    def __init__(self, message: str, status=409):
        super().__init__(message, status)


