import strawberry

from src.api.queries.user_query import UserQuery
from src.api.mutations.auth_mutation import AuthMutation

@strawberry.type
class Query(
    UserQuery
): pass

@strawberry.type
class Mutation(
    AuthMutation 
) : pass

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
