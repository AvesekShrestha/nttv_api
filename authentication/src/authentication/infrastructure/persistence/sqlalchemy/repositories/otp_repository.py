from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authentication.application.interfaces.otp_repository_interface import IOTPRepository
from authentication.application.shared.datetime_provider_interface import IDateTimeProvider
from authentication.domain.otp.otp_aggregate import OTPAggregate
from authentication.infrastructure.persistence.sqlalchemy.mappers.opt_mapper import OTPMapper
from authentication.infrastructure.persistence.sqlalchemy.models.opt_model import OTP


class OTPRepository(IOTPRepository) : 

    def __init__(self, session : AsyncSession, datetime_provider : IDateTimeProvider) : 
        self.session = session
        self.datetime_provider = datetime_provider

    async def get_by_email(self, email: str) -> OTPAggregate | None:

        statement = (
            select(OTP)
            .where(
                OTP.email == email,
                OTP.expires_at > self.datetime_provider.now(),
                OTP.attempts < OTP.max_attempts,
                OTP.consumed_at.is_(None),
            )
            .order_by(OTP.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(statement=statement)

        otp = result.scalar_one_or_none()
        if otp is None : return None

        return OTPMapper.to_domain(otp)

    async def add(self, aggregate: OTPAggregate) -> OTPAggregate:

        otp = OTPMapper.to_model(aggregate)
        self.session.add(otp)
        await self.session.flush()

        return OTPMapper.to_domain(otp)

    async def update(self, aggregate: OTPAggregate) -> OTPAggregate:

        otp = OTPMapper.to_model(aggregate)
        self.session.add(otp)
        await self.session.flush()

        return OTPMapper.to_domain(otp)



