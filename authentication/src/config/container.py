from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector import containers, providers


from src.application.auth.auth_service import AuthService
from src.application.category.category_service import CategoryService
from src.application.team.team_service import TeamService

from src.infrastructure.identity.hasher import Hasher
from src.infrastructure.identity.id_generator import IdGenerator
from src.infrastructure.identity.datetime_provider import DateTimeProvider
from src.infrastructure.identity.jwt_generator import JWTGenerator
from src.infrastructure.identity.refresh_token_generator import RefreshTokenGenerator
from src.infrastructure.persistence.sqlalchemy.repositories.outbox_repository import OutboxRepository
from src.infrastructure.persistence.sqlalchemy.repositories.token_repository import TokenRepository
from src.infrastructure.persistence.sqlalchemy.repositories.user_respository import UserRepository
from src.infrastructure.persistence.sqlalchemy.repositories.category_repository import CategoryRepository
from src.infrastructure.persistence.sqlalchemy.repositories.team_repository import TeamRepository
from src.infrastructure.persistence.sqlalchemy.unit_of_work import UnitOfWork

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    session = providers.Dependency(instance_of=AsyncSession)

    hasher = providers.Singleton(Hasher)
    id_genertor = providers.Singleton(IdGenerator)
    jwt_generator = providers.Singleton(JWTGenerator)
    refresh_token_generator = providers.Singleton(RefreshTokenGenerator)
    datetime_provider = providers.Singleton(DateTimeProvider)

    unit_of_work = providers.Factory(
        UnitOfWork,
        session=session
    )

    token_repository = providers.Factory(
        TokenRepository,
        session=session
    )

    user_repository = providers.Factory(
        UserRepository,
        session=session
    )

    category_repository = providers.Factory(
        CategoryRepository,
        session=session
    )

    team_repository = providers.Factory(
        TeamRepository,
        session=session
    )

    outbox_repository = providers.Factory(
        OutboxRepository,
        session=session
    )

    auth_service = providers.Factory(
        AuthService,
        user_repository=user_repository,
        token_repository=token_repository,
        outbox_repository=outbox_repository,
        hasher=hasher,
        id_generator=id_genertor,
        jwt_generator=jwt_generator,
        refresh_token_generator=refresh_token_generator,
        datetime_provider=datetime_provider,
        unit_of_work=unit_of_work
    )

    category_service = providers.Factory(
        CategoryService,
        category_repository=category_repository,
        id_generator=id_genertor,
        unit_of_work=unit_of_work
    )

    team_service = providers.Factory(
        TeamService,
        team_repository=team_repository,
        category_repository=category_repository,
        user_repository=user_repository,
        id_generator=id_genertor,
        unit_of_work=unit_of_work

    )



container = Container()
