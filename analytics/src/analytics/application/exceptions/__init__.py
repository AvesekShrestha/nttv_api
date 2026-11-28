from analytics.application.shared.application_exception import ApplicationException


class MissingRequiredAttributeException(ApplicationException):
    code = "MISSING_REQUIRED_ATTRIBUTE"

    def __init__(
        self, message: str = "Required attribute is missing or null in Kafka event"
    ):
        super().__init__(message=message, status=422)
