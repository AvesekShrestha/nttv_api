from abc import ABC, abstractmethod

from src.application.dto.category_dto import CategoryCreateDTO, CategoryResponseDTO, CategoryUpdateDTO

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
    ) -> list[CategoryResponseDTO]:
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
    ) -> None:
        pass
