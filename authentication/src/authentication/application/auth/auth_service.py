from datetime import date, datetime, timedelta
from operator import add

from authentication.application.dto.otp_dto import OTPResendDTO, OTPVerifyDTO
from authentication.application.events.otp_event import OTPResendEvent
from authentication.application.exceptions.otp_exceptions import OTPNotFound
from authentication.application.interfaces.otp_repository_interface import IOTPRepository
from authentication.application.shared.otp_generator_interface import IOTPGenerator
from authentication.config import settings

from authentication.domain.exceptions.otp_exceptions import InvalidOTP, OTPExpired
from authentication.domain.exceptions.refresh_token_expired_exception import ExpiredRefreshToken
from authentication.domain.otp.otp_aggregate import OTPAggregate
from authentication.domain.outbox.entity.outbox_event import OutboxEvent
from authentication.domain.token.token_aggregate import TokenAggregrate
from authentication.domain.users.user_role import UserRole
from authentication.domain.users.user_aggregrate import UserAggregrate

from authentication.application.auth.auth_service_interface import IAuthService
from authentication.application.dto.register_dto import RegisterDTO
from authentication.application.dto.user_response_dto import UserResponseDTO
from authentication.application.exceptions.user_exception import InactiveUser, UserAlreadyExists, UserNotFound
from authentication.application.interfaces.token_repository_interface import ITokenRepository
from authentication.application.interfaces.user_repository_interface import IUserRepository
from authentication.application.shared.hasher_interface import IHasher
from authentication.application.shared.id_generator_interface import IIdGenerator
from authentication.application.shared.jwt_generator_interface import IJWTGenerator
from authentication.application.mappers.auth_mapper import AuthMapper
from authentication.application.mappers.user_mapper import UserMapper
from authentication.application.dto.login_dto import LoginDTO
from authentication.application.dto.login_response_dto import LoginResponseDTO, LoginResultDTO
from authentication.application.dto.token_dto import AccessTokenResponseDTO
from authentication.application.events.user_created_event import UserCreatedEvent
from authentication.application.exceptions.already_logged_in_exception import AlreadyLoggedIn
from authentication.application.exceptions.authentication_exception import AuthenticationRequired
from authentication.application.exceptions.password_exception import InvalidPassword
from authentication.application.interfaces.outbox_repository_interface import IOutboxRepository
from authentication.application.shared.datetime_provider_interface import IDateTimeProvider
from authentication.application.shared.jwt_payload import JWTPayload
from authentication.application.shared.refresh_token_generator_interface import IRefreshTokenGenerator
from authentication.application.shared.unit_of_work_interface import IUnitOfWork



class AuthService(IAuthService):
    def __init__(
        self,
        user_repository: IUserRepository,
        token_repository: ITokenRepository,
        outbox_repository: IOutboxRepository,
        otp_repository : IOTPRepository,
        hasher: IHasher,
        id_generator: IIdGenerator,
        jwt_generator: IJWTGenerator,
        refresh_token_generator: IRefreshTokenGenerator,
        datetime_provider: IDateTimeProvider,
        otp_generator: IOTPGenerator,
        unit_of_work: IUnitOfWork
    ):
        self._user_repository = user_repository
        self._token_repository = token_repository
        self._outbox_repository = outbox_repository
        self._otp_repository = otp_repository
        self._hasher = hasher
        self._id_generator = id_generator
        self._jwt_generator = jwt_generator
        self._refresh_token_generator = refresh_token_generator
        self._datetime_provider = datetime_provider
        self._otp_generator = otp_generator
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

        otp_id = self._id_generator.generate_random_id()
        raw_otp = self._otp_generator.generate()

        otp : OTPAggregate = OTPAggregate.create(
            id=otp_id,
            email=user.email,
            otp_hash=await self._hasher.hash(raw_otp)
        )
        await self._otp_repository.add(otp)

        event_data : UserCreatedEvent = UserCreatedEvent(
            email=user.email,
            otp=raw_otp
        )
        event = OutboxEvent.create(
            key=user.id,
            event_id=self._id_generator.generate_event_id(),
            event_type="user.created",
            occurred_at=self._datetime_provider.now(),
            data=event_data.model_dump(mode="json")
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

    async def resend_otp(self, payload: OTPResendDTO) -> bool:
        existing_otp: OTPAggregate | None = (
            await self._otp_repository.get_by_email(payload.email)
        )

        if existing_otp is not None and existing_otp.is_usable(
            self._datetime_provider.now()
        ):
            existing_otp.mark_consumed()
            await self._otp_repository.update(existing_otp)

        raw_otp = self._otp_generator.generate()
        otp_id = self._id_generator.generate_random_id()

        new_otp = OTPAggregate.create(
            id=otp_id,
            email=payload.email,
            otp_hash=await self._hasher.hash(raw_otp),
        )

        event_data = OTPResendEvent(
            email=payload.email,
            otp=raw_otp,
        )

        event = OutboxEvent.create(
            key=otp_id,
            event_id=self._id_generator.generate_event_id(),
            event_type="otp.resend",
            occurred_at=self._datetime_provider.now(),
            data=event_data.model_dump(mode="json"),
        )

        await self._otp_repository.add(new_otp)
        await self._outbox_repository.add(event)

        await self._unit_of_work.commit()

        return True


    async def verify_otp(self, payload: OTPVerifyDTO) -> bool:
        otp: OTPAggregate | None = (
            await self._otp_repository.get_by_email(payload.email)
        )

        if otp is None:
            raise OTPNotFound("OTP not found")

        now = self._datetime_provider.now()

        if not otp.is_usable(now):
            raise OTPExpired("OTP is expired or no longer usable")

        verified = await self._hasher.verify(
            payload.otp,
            otp.otp_hash,
        )

        if not verified:
            otp.record_failed_attempt()

            await self._otp_repository.update(otp)
            await self._unit_of_work.commit()

            raise InvalidOTP("Invalid OTP")

        otp.mark_consumed()

        await self._otp_repository.update(otp)
        await self._unit_of_work.commit()

        return True
