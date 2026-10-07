from src.domain.shared.domain_exception import DomainException


class ExpiredRefreshToken(DomainException) :

    code : str = "REFRESH_TOKEN_EXPIRED"
    def __init__(self, message: str, status: int = 401) : 
        super().__init__(message, status)
