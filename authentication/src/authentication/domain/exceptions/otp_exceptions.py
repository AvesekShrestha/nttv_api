from authentication.domain.shared.domain_exception import DomainException

class OTPMaxLimitReached(DomainException) : 
    code = "OTP_LIMIT_REACHED"

    def __init__(self, message : str, status : int = 409):
        super().__init__(message=message, status=status)


class OTPExpired(DomainException) : 
    code = "OTP_EXPIRED"

    def __init__(self, message : str, status : int = 400):
        super().__init__(message=message, status=status)

class InvalidOTP(DomainException) : 
    code = "INVALID_OTP"

    def __init__(self, message : str, status : int = 400):
        super().__init__(message=message, status=status)


