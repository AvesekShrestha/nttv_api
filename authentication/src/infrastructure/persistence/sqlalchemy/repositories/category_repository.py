from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.category_repository_interface import ICategoryRepository
from src.domain.category.category_aggregrate import CategoryAggregrate
from src.infrastructure.persistence.sqlalchemy.mappers.category_infrastructure_mapper import CategoryMapper

from src.infrastructure.persistence.sqlalchemy.models.category_model import Category


class CategoryRepository(ICategoryRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        category_id: str,
    ) -> CategoryAggregrate | None:

        stmt = select(Category).where(Category.id == category_id)
        result = await self.session.execute(stmt)

        category = result.scalar_one_or_none()

        if category is None:
            return None

        return CategoryMapper.to_domain(category)

    async def get_all(
        self,
    ) -> list[CategoryAggregrate]:

        stmt = select(Category)
        result = await self.session.execute(stmt)

        categories = result.scalars().all()

        return [
            CategoryMapper.to_domain(category)
            for category in categories
        ]

    async def add(
        self,
        aggregate: CategoryAggregrate,
    ) -> CategoryAggregrate:

        category = CategoryMapper.to_model(aggregate)

        self.session.add(category)
        await self.session.commit()

        return CategoryMapper.to_domain(category)

    async def update(
        self,
        aggregate: CategoryAggregrate,
    ) -> CategoryAggregrate:

        category = CategoryMapper.to_model(aggregate)

        updated_category = await self.session.merge(category)
        await self.session.commit()

        return CategoryMapper.to_domain(updated_category)

    async def delete(
        self,
        category_id: str,
    ) -> None:

        stmt = delete(Category).where(Category.id == category_id)

        await self.session.execute(stmt)
        await self.session.commit()
