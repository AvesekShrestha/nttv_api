from abc import ABC, abstractmethod


from src.domain.category.category_aggregrate import CategoryAggregrate

class ICategoryRepository:

    @abstractmethod
    async def get_by_id(self, category_id : str) -> CategoryAggregrate | None : pass

    @abstractmethod
    async def get_all(self)-> list[CategoryAggregrate]: pass

    @abstractmethod
    async def add(self, aggregate: CategoryAggregrate) -> CategoryAggregrate: pass

    @abstractmethod
    async def update(self, aggregate: CategoryAggregrate) -> CategoryAggregrate: pass

    @abstractmethod
    async def delete(self, category_id : str) -> None: pass
