import strawberry

@strawberry.type
class UserQuery:

    @strawberry.field
    def health(self) -> str : 
        return "OK"
