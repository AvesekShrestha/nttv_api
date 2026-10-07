from fastapi import HTTPException, Request

from src.application.exceptions.authentication_exception import AuthenticationRequired


async def get_current_user(request: Request):
    user = getattr(request.state, "user", None)

    if user is None:
        raise AuthenticationRequired("Authentication is required")

    return user
