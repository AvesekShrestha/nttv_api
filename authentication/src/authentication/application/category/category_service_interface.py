from abc import ABC, abstractmethod

from authentication.application.dto.category_dto import CategoryCreateDTO, CategoryResponseDTO, CategoryUpdateDTO
from authentication.application.dto.category_query_dto import CategoryQueryDTO
from authentication.application.shared.pagination_response import PaginatedResponse

class ICategoryService(ABC):

    @abstractmethod
    async def get_by_id(
        self,
        category_id: str,
    ) -> CategoryResponseDTO | None:
        pass

    @abstractmethod
    async def get_all(
        self,
        query : CategoryQueryDTO
    ) -> PaginatedResponse[CategoryResponseDTO]:
        pass

    @abstractmethod
    async def create(
        self,
        payload: CategoryCreateDTO,
    ) -> CategoryResponseDTO:
        pass

    @abstractmethod
    async def update(
        self,
        category_id: str,
        payload: CategoryUpdateDTO,
    ) -> CategoryResponseDTO:
        pass

    @abstractmethod
    async def delete(
        self,
        category_id: str,
    ) -> bool:
        pass
