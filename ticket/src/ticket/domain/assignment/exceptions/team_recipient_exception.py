from ticket.domain.shared.domain_exception import DomainException

class InvalidRequest(DomainException):
    code = "INVALID_REQUEST"

    def __init__(self, message: str, status: int = 400):
        super().__init__(message, status)

class TeamAlreadyExists(DomainException):
    code = "TEAM_ALREADY_EXISTS"

    def __init__(self, message: str, status: int = 409):
        super().__init__(message, status)

