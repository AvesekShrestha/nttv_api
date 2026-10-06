import strawberry

from src.api.types.user_type import UserType

@strawberry.type
class LoginResponseType:
    user : UserType
    access_token: str
