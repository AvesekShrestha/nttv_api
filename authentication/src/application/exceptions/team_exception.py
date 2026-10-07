from src.application.shared.application_exception import ApplicationException


class TeamNotFound(ApplicationException):

    def __init__(self, message: str, status=500):
        super().__init__(message, status)
