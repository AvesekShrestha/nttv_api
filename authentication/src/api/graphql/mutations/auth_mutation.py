import strawberry

from src.api.resolvers.auth_resolver import register, login, logout, bootstrap

@strawberry.type
class AuthMutation:

    register = strawberry.mutation(resolver=register)
    login = strawberry.mutation(resolver=login)
    logout = strawberry.mutation(resolver=logout)
    bootstrap = strawberry.mutation(resolver=bootstrap)
