from ticket.application.shared.application_exception import ApplicationException

class EventAlreadyProcessed(ApplicationException) : 
    code: str = "ALREADY_PROCESSED"

    def __init__(self, message: str, status=400):
        super().__init__(message, status)
