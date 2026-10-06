from fastapi import Depends
from strawberry import Info

from src.api.types.login_response_type import LoginResponseType
from src.api.types.user_type import UserType
from src.application.mappers.user_mapper import UserMapper
from src.api.inputs.login_type import LoginInput

from src.application.auth.auth_service_interface import IAuthService
from src.application.dto.login_response_dto import LoginResponseDTO
from src.application.dto.user_response_dto import UserResponseDTO
from src.api.inputs.register_type import RegisterInput
from src.api.mappers.auth_api_mapper import AuthMapper
from src.api.mappers.user_api_mapper import UserMapper

from src.application.auth.auth_service import AuthService


async def register(
    input: RegisterInput,
) -> UserType:

    payload = AuthMapper.to_register_dto(input)

    user : UserResponseDTO = await auth_service.register(payload)
    return AuthMapper.to_register_graphql(user)

async def login(
    info: Info,
    input: LoginInput,
) -> LoginResponseType:

    request = info.context.request
    response = info.context.response

    payload = AuthMapper.to_login_dto(input)

    result : LoginResponseDTO = await auth_service.login(payload)

    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=7 * 24 * 60 * 60,
        path="/graphql/",
    )
    return AuthMapper.to_login_graphql(result)

async def logout(
    info: Info,
) -> bool:

    request = info.context.request
    response = info.context.response

    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        await auth_service.logout(refresh_token)

    response.delete_cookie(
        key="refresh_token",
        path="/graphql/",
    )
    return True

async def bootstrap() -> UserType : 

    result : UserResponseDTO = await auth_service.bootstrap()
    return UserMapper.to_graphql(result)

