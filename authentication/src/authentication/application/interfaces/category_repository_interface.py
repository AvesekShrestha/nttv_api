from abc import ABC, abstractmethod


from authentication.application.shared.pagination_response import PaginatedResponse
from authentication.domain.category.category_aggregrate import CategoryAggregrate

from authentication.application.dto.category_query_dto import CategoryQueryDTO

class ICategoryRepository:

    @abstractmethod
    async def get_by_id(self, category_id : str) -> CategoryAggregrate | None : pass

    @abstractmethod
    async def get_all(self, query : CategoryQueryDTO)-> PaginatedResponse[CategoryAggregrate]: pass

    @abstractmethod
    async def add(self, aggregate: CategoryAggregrate) -> CategoryAggregrate: pass

    @abstractmethod
    async def update(self, aggregate: CategoryAggregrate) -> CategoryAggregrate: pass

    @abstractmethod
    async def delete(self, category_id : str) -> None: pass
