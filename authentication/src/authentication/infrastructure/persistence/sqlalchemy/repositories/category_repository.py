from sqlalchemy import delete, select, func, or_, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from authentication.application.dto.category_query_dto import CategoryQueryDTO
from authentication.application.interfaces.category_repository_interface import ICategoryRepository
from authentication.application.shared.pagination_response import PaginatedResponse
from authentication.domain.category.category_aggregrate import CategoryAggregrate
from authentication.infrastructure.persistence.sqlalchemy.mappers.category_infrastructure_mapper import CategoryMapper

from authentication.infrastructure.persistence.sqlalchemy.models.category_model import Category


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
        query : CategoryQueryDTO
    ) -> PaginatedResponse[CategoryAggregrate]:

        filters = []


        if query.is_active is not None:
            filters.append(
                Category.is_active == query.is_active
            )

        if query.search is not None and query.search.strip():
            search_term = f"%{query.search.strip()}%"

            filters.append(
                or_(
                    Category.name.ilike(search_term),
                    Category.description.ilike(search_term),
                )
            )

        count_stmt = (
            select(func.count())
            .select_from(Category)
            .where(*filters)
        )

        total = await self.session.scalar(count_stmt)

        sort_columns = {
            "name": Category.name,
            "created_at": Category.created_at,
            "updated_at": Category.updated_at,
        }

        sort_column = sort_columns[query.sort_by]

        if query.sort_order == "asc":

            ordering = asc(sort_column)
        else:
            ordering = desc(sort_column)

        offset = (query.page - 1) * query.limit

        stmt = (
            select(Category)
            .where(*filters)
            .order_by(ordering, Category.created_at)
            .offset(offset)
            .limit(query.limit)
        )

        result = await self.session.execute(stmt)

        teams = result.scalars().all()

        return PaginatedResponse(
            items=[
                CategoryMapper.to_domain(model=team)
                for team in teams
            ],
            total=total or 0,
            page=query.page,
            limit=query.limit,
        )

    async def add(
        self,
        aggregate: CategoryAggregrate,
    ) -> CategoryAggregrate:

        category = CategoryMapper.to_model(aggregate)

        self.session.add(category)
        await self.session.flush()

        return CategoryMapper.to_domain(category)

    async def update(
        self,
        aggregate: CategoryAggregrate,
    ) -> CategoryAggregrate:

        category = CategoryMapper.to_model(aggregate)

        updated_category = await self.session.merge(category)
        await self.session.flush()

        return CategoryMapper.to_domain(updated_category)

    async def delete(
        self,
        category_id: str,
    ) -> None:

        stmt = delete(Category).where(Category.id == category_id)

        await self.session.execute(stmt)
        await self.session.flush()
