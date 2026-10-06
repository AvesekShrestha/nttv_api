from src.domain.token.token_aggregate import TokenAggregrate
from src.infrastructure.persistence.sqlalchemy.models.token_model import RefreshToken


class TokenMapper:

    @staticmethod
    def to_domain(model : RefreshToken) -> TokenAggregrate:
        return TokenAggregrate(
            _id=model.id,
            _token_hash=model.token_hash,
            _expires_at=model.expires_at,
            _user_id=model.user_id,
            _revoked_at=model.revoked_at,
        )

    @staticmethod
    def to_model(aggregate : TokenAggregrate) -> RefreshToken:
        return RefreshToken(
            id=aggregate.id,
            token_hash=aggregate.token_hash,
            expires_at=aggregate.expires_at,
            user_id=aggregate.user_id,
            revoked_at=aggregate.revoked_at,
        )
