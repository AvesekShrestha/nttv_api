from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.rest_api.dependencies.authentication import get_current_user
from src.api.rest_api.dependencies.authorization import require_roles
from src.application.dto.login_dto import LoginDTO
from src.application.dto.user_response_dto import UserResponseDTO
from src.application.exceptions.authentication_exception import AuthenticationRequired

from src.application.dto.register_dto import RegisterDTO
from src.application.auth.auth_service import AuthService 
from src.application.auth.auth_service_interface import IAuthService
from src.application.dto.register_dto import RegisterDTO
from src.application.dto.login_response_dto import LoginResponseDTO
from src.infrastructure.persistence.sqlalchemy.database import get_session
from src.infrastructure.persistence.sqlalchemy.repositories import user_respository
from src.infrastructure.persistence.sqlalchemy.repositories.user_respository import UserRepository

from src.config import settings
from src.config.container import container


router = APIRouter()

@router.post("/auth/register", response_model=UserResponseDTO)
async def register(payload : RegisterDTO, session : AsyncSession = Depends(get_session)):

    container.session.override(session)
    auth_service = container.auth_service()

    result = await auth_service.register(payload=payload)
    return result

@router.post("/auth/login", response_model=LoginResponseDTO)
async def login(payload : LoginDTO, response: Response, session : AsyncSession = Depends(get_session)):

    container.session.override(session)
    auth_service = container.auth_service()

    result : LoginResponseDTO = await auth_service.login(payload=payload)

    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * settings.REFRESH_EXPIRE_DAYS,
        path="/api/auth",
    )
    return result


@router.post("/auth/logout", response_model=bool)
async def logout(request : Request, response : Response, session : AsyncSession = Depends(get_session), _ = Depends(get_current_user)):

    container.session.override(session)
    auth_service = container.auth_service()

    refresh_token : str | None =  request.cookies.get("refresh_token")

    if not refresh_token: 
        raise AuthenticationRequired("Refresh token required")

    if(refresh_token):
        await auth_service.logout(refresh_token)

    response.delete_cookie(
        key="refresh_token",
        path="/api/auth",
    )
    return True

@router.post("/auth/refresh")
async def refresh(request : Request, response : Response, session = Depends(get_session)):

    refresh_token : str | None =  request.cookies.get("refresh_token")

    if not refresh_token: 
        raise AuthenticationRequired("Already loggout or missing refresh token")

    container.session.override(session)
    auth_service = container.auth_service()

    return await auth_service.refresh(refresh_token=refresh_token)

