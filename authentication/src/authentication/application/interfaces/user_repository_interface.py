from abc import ABC, abstractmethod

from authentication.domain.users.user_aggregrate import UserAggregrate

from authentication.application.dto.user_query_dto import UserQueryDTO
from authentication.application.shared.pagination_response import PaginatedResponse

class IUserRepository:

    @abstractmethod
    async def get_by_id(self, user_id : str) -> UserAggregrate | None: pass

    @abstractmethod
    async def get_by_email(self, email: str) -> UserAggregrate | None: pass

    @abstractmethod
    async def get_all(self, query : UserQueryDTO)-> PaginatedResponse[UserAggregrate]: pass

    @abstractmethod
    async def add(self, aggregate: UserAggregrate) -> UserAggregrate: pass

    @abstractmethod
    async def update(self, aggregate: UserAggregrate) -> UserAggregrate: pass

    @abstractmethod
    async def delete(self, user_id : str) -> None: pass
