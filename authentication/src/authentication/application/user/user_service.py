from sqlalchemy import update
from sqlalchemy.sql.functions import mode

from authentication.application.dto.user_response_dto import UserResponseDTO
from authentication.application.dto.create_staff_dto import CreateStaffDTO
from authentication.application.events.user_created_event import UserCreatedEvent
from authentication.application.interfaces.otp_repository_interface import IOTPRepository
from authentication.application.interfaces.outbox_repository_interface import IOutboxRepository
from authentication.application.shared.datetime_provider_interface import IDateTimeProvider
from authentication.application.shared.otp_generator_interface import IOTPGenerator
from authentication.application.shared.unit_of_work_interface import IUnitOfWork
from authentication.application.user.user_service_interface import IUserService
from authentication.application.exceptions.user_exception import UserNotFound, UserAlreadyExists

from authentication.domain.otp.otp_aggregate import OTPAggregate
from authentication.domain.outbox.entity.outbox_event import OutboxEvent
from authentication.domain.users.user_aggregrate import UserAggregrate
from authentication.infrastructure.persistence.sqlalchemy.repositories.user_respository import IUserRepository
from authentication.infrastructure.identity.id_generator import IIdGenerator
from authentication.infrastructure.identity.hasher import IHasher


class UserService(IUserService): 

    def __init__(
        self,
        user_repository : IUserRepository,
        outbox_repository : IOutboxRepository,
        otp_repository : IOTPRepository,
        id_generator : IIdGenerator,
        otp_generator : IOTPGenerator,
        hasher : IHasher,
        unit_of_work : IUnitOfWork,
        datetime_provider : IDateTimeProvider

    ) :
        self.user_repository = user_repository
        self.outbox_repository = outbox_repository
        self.otp_repository=otp_repository
        self.id_generator = id_generator
        self.otp_generator = otp_generator
        self.hasher = hasher
        self.unit_of_work = unit_of_work
        self.datetime_provider = datetime_provider

    async def get_by_id(self, user_id: str) -> UserResponseDTO:

        user = await self.user_repository.get_by_id(user_id=user_id)

        if user is None : 
            raise UserNotFound(f"User with id:{user_id} doesn't exists")

        return self._to_response(user)

    async def get_all(self) -> list[UserResponseDTO]:

        users = await self.user_repository.get_all()

        return [
            self._to_response(user)
            for user in users
        ]

    async def create_staff(self, payload: CreateStaffDTO) -> UserResponseDTO:

        user_id = self.id_generator.generate_user_id()

        existing_user = await self.user_repository.get_by_email(
            payload.email
        )

        if existing_user is not None:
            raise UserAlreadyExists("Email is already registered")

        hashed_password = await self.hasher.hash(
            payload.password
        )

        user = UserAggregrate.create(
            id=user_id,
            username=payload.username,
            email=payload.email,
            password=hashed_password,
            role=payload.role,
            level=payload.level
        )
        result : UserAggregrate = await self.user_repository.add(user)

        otp_id = self.id_generator.generate_random_id()
        raw_otp = self.otp_generator.generate()

        otp : OTPAggregate = OTPAggregate.create(
            id=otp_id,
            email=user.email,
            otp_hash=await self.hasher.hash(raw_otp)
        )
        await self.otp_repository.add(otp)

        event_data : UserCreatedEvent = UserCreatedEvent(
            email=user.email,
            otp=raw_otp
        )
        event = OutboxEvent.create(
            key=user.id,
            event_id=self.id_generator.generate_event_id(),
            event_type="user.created",
            occurred_at=self.datetime_provider.now(),
            data=event_data.model_dump(mode="json")
        )

        await self.outbox_repository.add(event)

        await self.unit_of_work.commit()
        return self._to_response(result)


    def _to_response(self, aggregate : UserAggregrate) -> UserResponseDTO : 
        return UserResponseDTO(
            id=aggregate.id,
            username=aggregate.username,
            email=aggregate.email,
            role=aggregate.role,
            level=aggregate.level,
            is_active=aggregate.is_active,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at
        )
