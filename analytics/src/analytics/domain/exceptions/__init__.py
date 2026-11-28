from analytics.domain.shared.domain_exception import DomainException


class InvalidDomainEventDataException(DomainException):
    code = "INVALID_DOMAIN_EVENT_DATA"

    def __init__(self, message: str = "Invalid domain event data received"):
        super().__init__(message=message, status=422)
