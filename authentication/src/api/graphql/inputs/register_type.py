import strawberry

@strawberry.input
class RegisterInput:
    username: str
    email: str
    password: str
