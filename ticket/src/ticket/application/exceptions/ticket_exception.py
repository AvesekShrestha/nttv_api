from ticket.application.shared.application_exception import ApplicationException

class TicketNotFound(ApplicationException) : 
    code: str = "TICKET_NOT_FOUND"

    def __init__(self, message: str, status=404):
        super().__init__(message, status)
