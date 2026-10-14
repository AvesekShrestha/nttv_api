from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import user

from api.rest_api.dependencies.authentication import get_current_user
from api.rest_api.dependencies.authorization import require_roles
from application.dto.login_dto import LoginDTO
from application.dto.user_response_dto import UserResponseDTO
from application.exceptions.authentication_exception import AuthenticationRequired

from application.dto.register_dto import RegisterDTO
from application.auth.auth_service import AuthService 
from application.auth.auth_service_interface import IAuthService
from application.dto.register_dto import RegisterDTO
from application.dto.login_response_dto import LoginResponseDTO, LoginResultDTO
from infrastructure.persistence.sqlalchemy.database import get_session
from infrastructure.persistence.sqlalchemy.repositories import user_respository
from infrastructure.persistence.sqlalchemy.repositories.user_respository import UserRepository

from config import settings
from config.container import container


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

    result : LoginResultDTO = await auth_service.login(payload=payload)

    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * settings.REFRESH_EXPIRE_DAYS,
        path="/api/auth",
    )
    return LoginResponseDTO(
        user=result.user,
        access_token=result.access_token
    )

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

