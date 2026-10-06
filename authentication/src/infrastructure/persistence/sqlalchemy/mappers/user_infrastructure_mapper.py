from src.domain.shared.level import Level
from src.domain.users.user_aggregrate import UserAggregrate
from src.domain.users.user_role import UserRole
from src.infrastructure.persistence.sqlalchemy.models.user_model import User


class UserMapper:

    @staticmethod
    def to_domain(model: User) -> UserAggregrate:
        return UserAggregrate(
            _id=model.id,
            _username=model.username,
            _email=model.email,
            _password=model.password,
            _role=UserRole.from_string(model.role),
            _level=Level.from_string(model.level) if model.level else None,
            _is_active=model.is_active,
            _created_at=model.created_at,
            _updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(aggregate: UserAggregrate) -> User:
        return User(
            id=aggregate.id,
            username=aggregate.username,
            email=aggregate.email,
            password=aggregate.password,
            role=aggregate.role.value,
            level=aggregate.level.value if aggregate.level else None,
            is_active=aggregate.is_active,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
