from ticket.domain.shared.domain_exception import DomainException

class ActivityNotFound(DomainException):
    code = "ACTIVITY_NOT_FOUND"

    def __init__(self, message: str, status : int = 404):
        super().__init__(message=message, status=status)
