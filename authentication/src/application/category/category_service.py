from src.application.dto.category_dto import CategoryCreateDTO, CategoryResponseDTO, CategoryUpdateDTO
from src.application.exceptions.category_exception import CategoryDoesNotExists
from src.application.interfaces.category_repository_interface import ICategoryRepository
from src.application.category.category_service_interface import ICategoryService

from src.domain.category.category_aggregrate import CategoryAggregrate


class CategoryService(ICategoryService):

    def __init__(
        self,
        category_repository: ICategoryRepository,
        id_generator,
    ):
        self.category_repository = category_repository
        self.id_generator = id_generator

    async def get_by_id(
        self,
        category_id: str,
    ) -> CategoryResponseDTO | None:

        category = await self.category_repository.get_by_id(
            category_id=category_id,
        )

        if category is None:
            raise CategoryDoesNotExists(f"No such category with id : {category_id}") 
        return self._to_response(category)

    async def get_all(
        self,
    ) -> list[CategoryResponseDTO]:

        categories = await self.category_repository.get_all()

        return [
            self._to_response(category)
            for category in categories
        ]

    async def create(
        self,
        payload: CategoryCreateDTO,
    ) -> CategoryResponseDTO:

        category = CategoryAggregrate.create(
            id=self.id_generator.generate_category_id(),
            name=payload.name,
            description=payload.description,
        )

        category = await self.category_repository.add(
            aggregate=category,
        )

        return self._to_response(category)

    async def update(
        self,
        category_id: str,
        payload: CategoryUpdateDTO,
    ) -> CategoryResponseDTO:

        category = await self.category_repository.get_by_id(
            category_id=category_id,
        )

        if category is None:
            # Replace with your own CategoryNotFound exception.
            raise ValueError("Category not found")

        category.change_name(payload.name)
        category.change_description(payload.description)

        category = await self.category_repository.update(
            aggregate=category,
        )

        return self._to_response(category)

    async def delete(
        self,
        category_id: str,
    ) -> None:

        category = await self.category_repository.get_by_id(
            category_id=category_id,
        )

        if category is None:
            raise CategoryDoesNotExists("Category not found")

        await self.category_repository.delete(
            category_id=category_id,
        )

    @staticmethod
    def _to_response(
        category: CategoryAggregrate,
    ) -> CategoryResponseDTO:

        return CategoryResponseDTO(
            id=category.id,
            name=category.name,
            description=category.description,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )
