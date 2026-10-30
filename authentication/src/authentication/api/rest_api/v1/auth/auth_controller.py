from fastapi import APIRouter, Depends, Request, Response
import pydantic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import user

from authentication.api.rest_api.v1.dependencies.authentication import get_current_user
from authentication.api.rest_api.v1.dependencies.authorization import require_roles
from authentication.application.auth import auth_service
from authentication.application.dto.login_dto import LoginDTO
from authentication.application.dto.otp_dto import OTPResendDTO, OTPVerifyDTO
from authentication.application.dto.user_response_dto import UserResponseDTO
from authentication.application.exceptions.authentication_exception import AuthenticationRequired

from authentication.application.dto.register_dto import RegisterDTO
from authentication.application.auth.auth_service import AuthService 
from authentication.application.auth.auth_service_interface import IAuthService
from authentication.application.dto.register_dto import RegisterDTO
from authentication.application.dto.login_response_dto import LoginResponseDTO, LoginResultDTO
from authentication.infrastructure.persistence.sqlalchemy.database import get_session
from authentication.infrastructure.persistence.sqlalchemy.repositories import user_respository
from authentication.infrastructure.persistence.sqlalchemy.repositories.user_respository import UserRepository

from authentication.config import settings
from authentication.config.container import container


router = APIRouter()

@router.post("/register", response_model=UserResponseDTO)
async def register(payload : RegisterDTO, session : AsyncSession = Depends(get_session)):

    container.session.override(session)
    auth_service = container.auth_service()

    result = await auth_service.register(payload=payload)
    return result

@router.post("/login", response_model=LoginResponseDTO)
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
        path="/api/v1/auth",
    )
    return LoginResponseDTO(
        user=result.user,
        access_token=result.access_token
    )

@router.post("/logout", response_model=bool)
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

@router.post("/refresh")
async def refresh(request : Request, response : Response, session = Depends(get_session)):

    refresh_token : str | None =  request.cookies.get("refresh_token")

    if not refresh_token: 
        raise AuthenticationRequired("Already loggout or missing refresh token")

    container.session.override(session)
    auth_service = container.auth_service()

    return await auth_service.refresh(refresh_token=refresh_token)

@router.post("/resend-otp", response_model=bool)
async def resend_otp(payload : OTPResendDTO, session : AsyncSession = Depends(get_session)):

    container.session.override(session)
    auth_service = container.auth_service()

    result = await auth_service.resend_otp(payload=payload)

    return result


@router.post("/verify-otp", response_model=bool)
async def verify_otp(payload : OTPVerifyDTO, session : AsyncSession = Depends(get_session)) : 

    container.session.override(session)
    auth_service = container.auth_service()

    result = await auth_service.verify_otp(payload=payload)

    return result
