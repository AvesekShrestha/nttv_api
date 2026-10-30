from authentication.application.shared.application_exception import ApplicationException

class OTPNotFound(ApplicationException) :
    code = "OTP_NOT_FOUND"

    def __init__(self, message: str, status=404):
        super().__init__(message, status)

class OTPExpired(ApplicationException) :
    code = "OTP_EXPIREDJKJJJ"

    def __init__(self, message: str, status=404):
        super().__init__(message, status)
