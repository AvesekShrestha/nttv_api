from analytics.application.shared.application_exception import ApplicationException


class ResourceNotFoundException(ApplicationException):
    code = "RESOURCE_NOT_FOUND"

    def __init__(self, message: str = "Requested resource not found"):
        super().__init__(message=message, status=404)


class InvalidQueryParameterException(ApplicationException):
    code = "INVALID_QUERY_PARAMETER"

    def __init__(self, message: str = "Invalid query parameters provided"):
        super().__init__(message=message, status=400)
