from datetime import date, datetime, timedelta
from os.path import exists

from graphql import Token

from src.application.dto.login_dto import LoginDTO
from src.application.dto.login_response_dto import LoginResponseDTO, LoginResultDTO
from src.application.dto.token_dto import AccessTokenResponseDTO
from src.application.exceptions.already_logged_in_exception import AlreadyLoggedIn
from src.application.exceptions.authentication_exception import AuthenticationRequired
from src.application.exceptions.password_exception import InvalidPassword
from src.application.interfaces.outbox_repository_interface import IOutboxRepository
from src.application.shared.datetime_provider_interface import IDateTimeProvider
from src.application.shared.jwt_payload import JWTPayload
from src.application.shared.refresh_token_generator_interface import IRefreshTokenGenerator
from src.application.shared.unit_of_work_interface import IUnitOfWork
from src.config import settings
from src.domain.exceptions.refresh_token_expired_exception import ExpiredRefreshToken
from src.domain.outbox.entity.outbox_event import OutboxEvent
from src.domain.token.token_aggregate import TokenAggregrate
from src.domain.users.user_role import UserRole
from src.application.auth.auth_service_interface import IAuthService
from src.application.dto.register_dto import RegisterDTO
from src.application.dto.user_response_dto import UserResponseDTO
from src.application.exceptions.user_exception import InactiveUser, UserAlreadyExists, UserNotFound
from src.application.interfaces.token_repository_interface import ITokenRepository
from src.application.interfaces.user_repository_interface import IUserRepository
from src.application.shared.hasher_interface import IHasher
from src.application.shared.id_generator_interface import IIdGenerator
from src.application.shared.jwt_generator_interface import IJWTGenerator
from src.domain.users.user_aggregrate import UserAggregrate
from src.application.mappers.auth_mapper import AuthMapper, UserMapper

class AuthService(IAuthService):
    def __init__(
        self,
        user_repository: IUserRepository,
        token_repository: ITokenRepository,
        outbox_repository: IOutboxRepository,
        hasher: IHasher,
        id_generator: IIdGenerator,
        jwt_generator: IJWTGenerator,
        refresh_token_generator: IRefreshTokenGenerator,
        datetime_provider: IDateTimeProvider,
        unit_of_work: IUnitOfWork
    ):
        self._user_repository = user_repository
        self._token_repository = token_repository
        self._outbox_repository = outbox_repository
        self._hasher = hasher
        self._id_generator = id_generator
        self._jwt_generator = jwt_generator
        self._refresh_token_generator = refresh_token_generator
        self._datetime_provider = datetime_provider
        self._unit_of_work = unit_of_work

    async def register(
        self,
        payload: RegisterDTO,
    ) -> UserResponseDTO:

        existing_user = await self._user_repository.get_by_email(
            payload.email
        )

        if existing_user is not None:
            raise UserAlreadyExists("Email is already registered")

        hashed_password = await self._hasher.hash(
            payload.password
        )

        user: UserAggregrate = UserAggregrate.create(
            id=self._id_generator.generate_user_id(),
            username=payload.username,
            email=payload.email,
            password=hashed_password,
        )

        result : UserAggregrate = await self._user_repository.add(user)

        event = OutboxEvent.create(
            event_id=self._id_generator.generate_event_id(),
            event_type="user.created",
            occurred_at=self._datetime_provider.now(),
            data={
                "username" : user.username,
                "email" : user.email
            }
        )

        await self._outbox_repository.add(event)

        await self._unit_of_work.commit()
        return UserMapper.to_response(result)

    async def login(
        self,
        payload: LoginDTO,
    ) -> LoginResultDTO:

        user = await self._user_repository.get_by_email(
            payload.email
        )

        if user is None:
            raise UserNotFound("Invalid email or password")

        already_logged_in = await self._token_repository.has_active_token(user_id=user.id)
        if already_logged_in: raise AlreadyLoggedIn("Already logged in. first logout")

        if not await self._hasher.verify(
            payload.password,
            user.password,
        ):
            raise InvalidPassword("Invalid email or password")

        if not user.is_active:
            raise InactiveUser("User account is inactive")

        now = self._datetime_provider.now()
        jwt_payload : JWTPayload = JWTPayload(
            sub=user.id,
            role=user.role,
            iat=now,
            exp=now + timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES)
        )
        access_token = await self._jwt_generator.generate(jwt_payload)
        
        refresh_token_id = self._id_generator.generate_refresh_token_id()
        refresh_token = self._refresh_token_generator.generate(refresh_token_id)
        refresh_token_hash = await self._hasher.hash(refresh_token)
        refresh_token_aggregate : TokenAggregrate = TokenAggregrate.create(
            refresh_token_id,
            refresh_token_hash,
            user_id=user.id,
            expires_at=self._datetime_provider.now() + timedelta(days=settings.REFRESH_EXPIRE_DAYS)
        )
        await self._token_repository.add(refresh_token_aggregate)

        await self._unit_of_work.commit()
        return AuthMapper.login_response(user, access_token=access_token, refresh_token=refresh_token)

    async def logout(self, refresh_token : str) -> bool:
        
        token_id, secret = refresh_token.split(".", 1)
        token : TokenAggregrate | None = await self._token_repository.get_by_id(token_id=token_id)

        if token is None:
            raise AuthenticationRequired("authentication required")

        valid_token = await self._hasher.verify(refresh_token, token.token_hash)

        if not valid_token: raise AuthenticationRequired("Invalid refresh token")
        if token.is_revoked: raise AuthenticationRequired("Refresh token already revoked")

        token.revoke()

        await self._token_repository.update(token)
        await self._unit_of_work.commit()

        return True

    async def refresh(self, refresh_token: str) -> AccessTokenResponseDTO : 

        token_id, secret = refresh_token.split(".", 1)
        token : TokenAggregrate | None = await self._token_repository.get_by_id(token_id=token_id)

        if token is None:
            raise AuthenticationRequired("Authentication required")

        valid_token = await self._hasher.verify(refresh_token, token.token_hash)

        if not valid_token:
            raise AuthenticationRequired("Invalid refresh token")

        if token.is_revoked:
            raise AuthenticationRequired("Invalid refresh token/ token has already been revoked")

        if token.is_expired:
            raise ExpiredRefreshToken("Refresh token has expired")

        user : UserAggregrate | None = await self._user_repository.get_by_id(user_id=token.user_id)
        if not user : raise AuthenticationRequired("Invalid refresh token")

        now = self._datetime_provider.now()
        jwt_payload : JWTPayload = JWTPayload(
            sub=user.id,
            role=user.role,
            iat=now,
            exp=now + timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES)
        )
        access_token = await self._jwt_generator.generate(jwt_payload)
        return AccessTokenResponseDTO(access_token=access_token)
