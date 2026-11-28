from analytics.domain.shared.domain_exception import DomainException


class InvalidEntityStateDomainException(DomainException):
    code = "INVALID_ENTITY_STATE"

    def __init__(self, message: str = "The entity is in an invalid state"):
        super().__init__(message=message, status=422)


class BusinessRuleViolationDomainException(DomainException):
    code = "BUSINESS_RULE_VIOLATION"

    def __init__(self, message: str = "A domain business rule was violated"):
        super().__init__(message=message, status=422)
