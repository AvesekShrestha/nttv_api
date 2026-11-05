from ticket.domain.shared.domain_exception import DomainException

class AgentAlreadyExists(DomainException):
    code = "AGENT_ALREADY_EXISTS"

    def __init__(self, message: str, status: int = 400):
        super().__init__(message, status)

class AgentNotFound(DomainException) : 
    code = "AGENT_NOT_FOUND"

    def __init__(self, message: str, status: int = 404):
        super().__init__(message, status)

class AlreadyClaimed(DomainException) : 
    code = "ALREADY_CLAIMED"

    def __init__(self, message: str, status: int = 409):
        super().__init__(message, status)

class NotEligiableToClaim(DomainException) : 
    code = "NOT_ELIGIABLE_TO_CLAIM"

    def __init__(self, message: str, status: int = 400):
        super().__init__(message, status)

class NotAvailableToClaim(DomainException) : 
    code = "NOT_AVAILABLE_TO_CLAIM"

    def __init__(self, message: str, status: int = 400):
        super().__init__(message, status)


