import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field, StrictBool


bearer = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
    )

    id: str = Field(min_length=1, strict=True)
    is_active: StrictBool


def authentication_required(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def authenticate_access_token(
    token: str,
    client: httpx.AsyncClient,
) -> CurrentUser:
    if not token.strip():
        raise authentication_required("Bearer token required")

    try:
        response = await client.get(
            "/api/v1/user/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        ) from None

    if response.status_code in (401, 403):
        raise authentication_required(
            "Invalid or expired access token"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        )

    try:
        user = CurrentUser.model_validate(response.json())

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Invalid authentication service response",
        ) from None

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> CurrentUser:
    if credentials is None:
        raise authentication_required("Bearer token required")

    return await authenticate_access_token(
        credentials.credentials,
        request.app.state.authentication_http_client,
    )
