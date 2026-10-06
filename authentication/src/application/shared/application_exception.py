class ApplicationException(Exception) : 

    code : str = "APPLICATION_EXCEPTION"
    def __init__(self, message: str, status= 500):
        super().__init__(message)
