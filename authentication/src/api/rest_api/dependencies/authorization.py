from fastapi import Request

from src.application.exceptions.authentication_exception import AuthenticationRequired
from src.application.exceptions.authorization_exception import AuthorizationRequired

def require_roles(*roles: str):

    async def dependency(request: Request):
        user = getattr(request.state, "user", None)

        if user is None:
            raise AuthenticationRequired(
                "Authentication is required"
            )

        user_role = user.role.lower()
        allowed_roles = {role.lower() for role in roles}

        if user_role not in allowed_roles:
            raise AuthorizationRequired(
                "Insufficient access"
            )

        return user

    return dependency
