from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector import containers, providers

from src.infrastructure.identity.hasher import Hasher
from src.infrastructure.identity.id_generator import IdGenerator
from src.infrastructure.identity.datetime_provider import DateTimeProvider
from src.infrastructure.identity.jwt_generator import JWTGenerator

from src.application.auth.auth_service import AuthService

from src.infrastructure.persistence.sqlalchemy.repositories.token_repository import TokenRepository
from src.infrastructure.persistence.sqlalchemy.repositories.user_respository import UserRepository
from src.infrastructure.identity.refresh_token_generator import RefreshTokenGenerator


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    session = providers.Dependency(instance_of=AsyncSession)

    hasher = providers.Singleton(Hasher)
    id_genertor = providers.Singleton(IdGenerator)
    jwt_generator = providers.Singleton(JWTGenerator)
    refresh_token_generator = providers.Singleton(RefreshTokenGenerator)
    datetime_provider = providers.Singleton(DateTimeProvider)

    token_repository = providers.Factory(
        TokenRepository,
        session=session
    )

    user_repository = providers.Factory(
        UserRepository,
        session=session
    )

    auth_service = providers.Factory(
        AuthService,
        user_repository=user_repository,
        token_repository=token_repository,
        hasher=hasher,
        id_generator=id_genertor,
        jwt_generator=jwt_generator,
        refresh_token_generator=refresh_token_generator,
        datetime_provider=datetime_provider
    )


container = Container()
