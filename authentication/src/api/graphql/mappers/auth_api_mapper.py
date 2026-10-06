from src.api.types.login_response_type import LoginResponseType
from src.api.types.user_type import UserType
from src.application.dto.login_response_dto import LoginResponseDTO
from src.application.dto.register_dto import RegisterDTO
from src.application.dto.user_response_dto import UserResponseDTO
from src.api.inputs.login_type import LoginInput
from src.api.inputs.register_type import RegisterInput
from src.application.dto.login_dto import LoginDTO


class AuthMapper:

    @staticmethod
    def to_login_dto(input: LoginInput) -> LoginDTO:
        return LoginDTO(
            email=input.email,
            password=input.password,
        )

    @staticmethod
    def to_login_graphql(input: LoginResponseDTO) -> LoginResponseType:
        return LoginResponseType(
            user=UserType(
                id=input.user.id,
                username=input.user.username,
                email=input.user.email,
                level=input.user.level,
                role=input.user.role,
                is_active=input.user.is_active,
                created_at=input.user.created_at,
                updated_at=input.user.updated_at
            ),
            access_token=input.access_token
        )

    @staticmethod
    def to_register_dto(input: RegisterInput) -> RegisterDTO:
        return RegisterDTO(
            username=input.username,
            email=input.email,
            password=input.password,
        )

    @staticmethod
    def to_register_graphql(input: UserResponseDTO) -> UserType:
        return UserType(
            id=input.id,
            username=input.username,
            email=input.email,
            level=input.level,
            role=input.role,
            is_active=input.is_active,
            created_at=input.created_at,
            updated_at=input.updated_at
        )
