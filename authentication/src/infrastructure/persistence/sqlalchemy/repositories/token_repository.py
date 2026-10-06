from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.sqlalchemy.mappers.token_infrastructure_mapper import TokenMapper
from src.application.interfaces.token_repository_interface import ITokenRepository

from src.domain.token.token_aggregate import TokenAggregrate

from src.infrastructure.persistence.sqlalchemy.mappers.user_infrastructure_mapper import UserMapper
from src.infrastructure.persistence.sqlalchemy.models.token_model import RefreshToken



class TokenRepository(ITokenRepository):

    def __init__(self, session : AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, token_id: str) -> TokenAggregrate | None:

        statement = select(RefreshToken).where(RefreshToken.id == token_id)
        result = await self.session.execute(statement=statement)

        token = result.scalar_one_or_none()

        if token is None:
            return None

        return TokenMapper.to_domain(token)


    async def add(self, aggregrate: TokenAggregrate)-> TokenAggregrate:

        refresh_token : RefreshToken = TokenMapper.to_model(aggregrate)
        self.session.add(refresh_token)
        await self.session.commit()

        return TokenMapper.to_domain(refresh_token)

    async def update(self, aggregate : TokenAggregrate):

        token = TokenMapper.to_model(aggregate)
        updated_token = await self.session.merge(token)

        await self.session.commit()


