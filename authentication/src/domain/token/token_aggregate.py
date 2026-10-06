from dataclasses import dataclass
from datetime import datetime, timezone

from src.domain.shared.aggregrate import AggregrateRoot
from src.domain.exceptions.refresh_token_expired_exception import RefreshTokenExpired

@dataclass
class TokenAggregrate(AggregrateRoot[str]):

    _token_hash: str
    _expires_at: datetime
    _user_id: str
    _revoked_at: datetime | None = None

    @property
    def token_hash(self) -> str:
        return self._token_hash

    @property
    def expires_at(self) -> datetime:
        return self._expires_at

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def revoked_at(self) -> datetime | None:
        return self._revoked_at

    @property
    def is_revoked(self) -> bool:
        return self._revoked_at is not None

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self._expires_at

    @staticmethod
    def create(
        id: str,
        token_hash: str,
        user_id: str,
        expires_at: datetime,
    ) -> "TokenAggregrate":

        return TokenAggregrate(
            _id=id,
            _token_hash=token_hash,
            _user_id=user_id,
            _expires_at=expires_at,
        )

    def revoke(self) -> None:

        if self.is_revoked:
            raise RefreshTokenExpired(
                "Refresh token has already been revoked"
            )

        if self.is_expired:
            raise RefreshTokenExpired(
                "Refresh token has expired"
            )

        self._revoked_at = datetime.now(timezone.utc)


