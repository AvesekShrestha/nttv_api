from ticket.domain.shared.domain_exception import DomainException

class AssignmentAlreadyTerminated(DomainException):
    code = "ALREADY_TERMINATED"

    def __init__(self, message: str, status: int = 400):
        super().__init__(message, status)

class AssignmentAlreadyStarted(DomainException):
    code = "ALREADY_STARTED"

    def __init__(self, message: str, status: int = 400):
        super().__init__(message, status)

class AssignmentIncompletable(DomainException):
    code = "ASSIGNMENT_INCOMPLETABLE"

    def __init__(self, message: str, status: int = 400):
        super().__init__(message, status)

class IneligibleRecipient(DomainException):
    code = "INELIGIBLE_RECIPIENT"

    def __init__(self, message: str, status: int = 400):
        super().__init__(message, status)

class AssignmentNotFound(DomainException):
    code = "ASSIGNMENT_NOT_FOUND"

    def __init__(self, message: str, status: int = 404):
        super().__init__(message, status)

class InvalidReassignmentRequest(DomainException):
    code = "INVALID_REASSIGNMENT_REQUEST"

    def __init__(self, message: str, status: int = 400):
        super().__init__(message, status)

class InitialAssignmentNotFound(DomainException) :
    code: str = "INITIAL_ASSIGNMENT_NOT_FOUND"

    def __init__(self, message: str, status=404):
        super().__init__(message, status)

