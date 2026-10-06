from src.api.types.user_type import UserType
from src.application.dto.user_response_dto import UserResponseDTO


class UserMapper:

    @staticmethod
    def to_graphql(input: UserResponseDTO) -> UserType:
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

