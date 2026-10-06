from inspect import trace

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto.login_dto import LoginDTO
from src.application.dto.user_response_dto import UserResponseDTO
from src.config.container import container

from src.application.dto.register_dto import RegisterDTO
from src.application.auth.auth_service import AuthService 
from src.application.auth.auth_service_interface import IAuthService
from src.application.dto.register_dto import RegisterDTO
from src.application.dto.login_response_dto import LoginResponseDTO
from src.infrastructure.persistence.sqlalchemy.database import get_session
from src.infrastructure.persistence.sqlalchemy.repositories import user_respository
from src.infrastructure.persistence.sqlalchemy.repositories.user_respository import UserRepository

from src.config import settings


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
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * settings.REFRESH_EXPIRE_DAYS,
        path="/auth",
    )
    return result
    
@router.post("/auth/logout", response_model=bool)
async def logout(response : Response, refresh_token : str | None = None, session : AsyncSession = Depends(get_session)):

    container.session.override(session)
    auth_service = container.auth_service()

    response.delete_cookie(
        key="refresh_token",
        path="/auth",
    )

    if(refresh_token):
        await auth_service.logout(refresh_token)

    return True


