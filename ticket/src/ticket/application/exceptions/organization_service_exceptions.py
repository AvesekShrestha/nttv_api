from ticket.application.shared.application_exception import ApplicationException

class OrganizationServiceException(ApplicationException) : 
    code = "ORGANIZATION_SERVICE_EXCEPTION"

    def __init__(self, message: str, status=500):
        super().__init__(message, status)
