from src.application.dto.user_response_dto import UserResponseDTO
from src.domain.users.user_aggregrate import UserAggregrate


class UserMapper:

    @staticmethod
    def to_response(aggregate : UserAggregrate) -> UserResponseDTO:
        return UserResponseDTO(
            id=aggregate.id,
            username=aggregate.username,
            email=aggregate.email,
            role=aggregate.role.value,
            level=aggregate.level.value if aggregate.level else None,
            is_active=aggregate.is_active,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at
        )
