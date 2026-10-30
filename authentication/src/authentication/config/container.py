import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector import containers, providers


from authentication.application.auth.auth_service import AuthService
from authentication.application.category.category_service import CategoryService
from authentication.application.team.team_service import TeamService

from authentication.application.user.user_service import UserService
from authentication.infrastructure.identity.hasher import Hasher
from authentication.infrastructure.identity.id_generator import IdGenerator
from authentication.infrastructure.identity.datetime_provider import DateTimeProvider
from authentication.infrastructure.identity.jwt_generator import JWTGenerator
from authentication.infrastructure.identity.otp_generator import OTPGenerator
from authentication.infrastructure.identity.refresh_token_generator import RefreshTokenGenerator
from authentication.infrastructure.persistence.sqlalchemy.repositories.otp_repository import OTPRepository
from authentication.infrastructure.persistence.sqlalchemy.repositories.outbox_repository import OutboxRepository
from authentication.infrastructure.persistence.sqlalchemy.repositories.token_repository import TokenRepository
from authentication.infrastructure.persistence.sqlalchemy.repositories.user_respository import UserRepository
from authentication.infrastructure.persistence.sqlalchemy.repositories.category_repository import CategoryRepository
from authentication.infrastructure.persistence.sqlalchemy.repositories.team_repository import TeamRepository
from authentication.infrastructure.persistence.sqlalchemy.unit_of_work import UnitOfWork
from authentication.infrastructure.messaging.kafka.producer import KafkaProducer
from authentication.infrastructure.workers.outbox_worker import OutboxWorker

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    session = providers.Dependency(instance_of=AsyncSession)

    hasher = providers.Singleton(Hasher)
    id_generator = providers.Singleton(IdGenerator)
    jwt_generator = providers.Singleton(JWTGenerator)
    refresh_token_generator = providers.Singleton(RefreshTokenGenerator)
    datetime_provider = providers.Singleton(DateTimeProvider)
    producer = providers.Singleton(KafkaProducer)
    otp_generator = providers.Singleton(OTPGenerator)

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

    otp_repository = providers.Factory(
        OTPRepository,
        session=session,
        datetime_provider=datetime_provider
    )

    user_repository = providers.Factory(
        UserRepository,
        session=session
    )

    auth_service = providers.Factory(
        AuthService,
        user_repository=user_repository,
        token_repository=token_repository,
        outbox_repository=outbox_repository,
        otp_repository=otp_repository,
        hasher=hasher,
        id_generator=id_generator,
        jwt_generator=jwt_generator,
        refresh_token_generator=refresh_token_generator,
        datetime_provider=datetime_provider,
        otp_generator=otp_generator,
        unit_of_work=unit_of_work
    )

    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
        outbox_repository=outbox_repository,
        otp_repository=otp_repository,
        id_generator=id_generator,
        otp_generator=otp_generator,
        hasher=hasher,
        unit_of_work=unit_of_work,
        datetime_provider=datetime_provider
    )

    category_service = providers.Factory(
        CategoryService,
        category_repository=category_repository,
        id_generator=id_generator,
        unit_of_work=unit_of_work
    )

    team_service = providers.Factory(
        TeamService,
        team_repository=team_repository,
        category_repository=category_repository,
        user_repository=user_repository,
        id_generator=id_generator,
        unit_of_work=unit_of_work

    )

    outbox_worker = providers.Singleton(
        OutboxWorker,
        producer=producer,
        outbox_repository=outbox_repository,
        datetime_provider=datetime_provider,
        unit_of_work=unit_of_work
    )

container = Container()
