from src.application.shared.application_exception import ApplicationException


class InvalidAccessToken(ApplicationException) : 
    code: str = "INVALID_ACCESS_TOKEN"

    def __init__(self, message: str, status=401):
        super().__init__(message, status)

class ExpiredAccessToken(ApplicationException) : 
    code: str = "EXPIRED_ACCESS_TOKEN"

    def __init__(self, message: str, status=401):
        super().__init__(message, status)
