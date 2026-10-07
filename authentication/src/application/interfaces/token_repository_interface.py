from abc import ABC, abstractmethod

from src.domain.token.token_aggregate import TokenAggregrate


class ITokenRepository(ABC):
    @abstractmethod
    async def get_by_id(self, token_id : str) -> TokenAggregrate | None : pass

    @abstractmethod
    async def add(self, aggregrate : TokenAggregrate) -> TokenAggregrate: pass

    @abstractmethod
    async def update(self, aggregate : TokenAggregrate) -> None: pass

    @abstractmethod
    async def has_active_token(self, user_id: str) -> bool: pass
