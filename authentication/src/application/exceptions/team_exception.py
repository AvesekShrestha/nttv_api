from src.application.shared.application_exception import ApplicationException


class TeamNotFound(ApplicationException):

    def __init__(self, message: str, status=404):
        super().__init__(message, status)

class TeamMemberAlreadyExists(ApplicationException):

    def __init__(self, message: str, status=409):
        super().__init__(message, status)

class TeamMemberDoesnotExists(ApplicationException):

    def __init__(self, message: str, status=409):
        super().__init__(message, status)

