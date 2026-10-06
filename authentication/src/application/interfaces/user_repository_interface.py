from abc import ABC, abstractmethod

from src.domain.users.user_aggregrate import UserAggregrate

class IUserRepository:

    @abstractmethod
    async def get_by_id(self, user_id : str) -> UserAggregrate | None: pass

    @abstractmethod
    async def get_by_email(self, email: str) -> UserAggregrate | None: pass

    @abstractmethod
    async def get_all(self)-> list[UserAggregrate]: pass

    @abstractmethod
    async def add(self, aggregate: UserAggregrate) -> UserAggregrate: pass

    @abstractmethod
    async def update(self, aggregate: UserAggregrate) -> UserAggregrate: pass

    @abstractmethod
    async def delete(self, user_id : str) -> None: pass
