from dataclasses import dataclass, field
from datetime import datetime, time, timedelta, timezone

from authentication.application import dto
from authentication.domain.exceptions.otp_exceptions import OTPMaxLimitReached
from authentication.domain.shared.aggregrate import AggregrateRoot

@dataclass
class OTPAggregate(AggregrateRoot[str]):

    _email : str
    _otp_hash : str
    _expires_at : datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=5))
    _attempts : int = 0
    _max_attempts : int = 3
    _consumed_at : datetime | None = None
    _created_at : datetime | None = None
    _last_sent_at : datetime | None = None


    @property
    def email(self) -> str:
        return self._email

    @property
    def otp_hash(self) -> str:
        return self._otp_hash

    @property
    def expires_at(self) -> datetime:
        return self._expires_at

    @property
    def attempts(self) -> int:
        return self._attempts

    @property
    def max_attempts(self) -> int:
        return self._max_attempts

    @property
    def consumed_at(self) -> datetime | None:
        return self._consumed_at

    @property
    def created_at(self) -> datetime | None:
        return self._created_at

    @property
    def last_sent_at(self) -> datetime | None:
        return self._last_sent_at


    def is_expired(self, now: datetime) -> bool:
        return now >= self._expires_at

    def is_consumed(self) -> bool:
        return self._consumed_at is not None

    def is_locked(self) -> bool:
        return self._attempts >= self._max_attempts

    def is_usable(self, now: datetime) -> bool:
        return (
            not self.is_expired(now)
            and not self.is_consumed()
            and not self.is_locked()
        )

    def record_failed_attempt(self) -> None:
        if self.is_locked():
            raise OTPMaxLimitReached("Maximum OTP attempts exceeded")

        self._attempts += 1

    def mark_consumed(
        self
    ) -> None:

        now = datetime.now(timezone.utc)
        self._consumed_at = now

    @staticmethod
    def create(
        id: str,
        email: str,
        otp_hash: str,
    ) -> "OTPAggregate":
        now = datetime.now(timezone.utc)

        return OTPAggregate(
            _id=id,
            _email=email,
            _otp_hash=otp_hash,
        )
