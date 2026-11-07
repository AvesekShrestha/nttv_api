from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, func, or_, asc, desc

from authentication.application.shared.pagination_response import PaginatedResponse
from authentication.domain.users.user_role import UserRole
from authentication.domain.users.user_aggregrate import UserAggregrate

from authentication.application.interfaces.user_repository_interface import IUserRepository
from authentication.application.dto.user_query_dto import UserQueryDTO

from authentication.infrastructure.persistence.sqlalchemy.models.user_model import User
from authentication.infrastructure.persistence.sqlalchemy.mappers.user_infrastructure_mapper import UserMapper


class UserRepository(IUserRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        user_id: str,
    ) -> UserAggregrate | None:

        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)

        user = result.scalar_one_or_none()

        if user is None:
            return None

        return UserMapper.to_domain(user)

    async def get_by_email(
        self,
        email: str,
    ) -> UserAggregrate | None:

        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)

        user = result.scalar_one_or_none()

        if user is None:
            return None

        return UserMapper.to_domain(user)

    async def get_all(
        self,
        query : UserQueryDTO
    ) -> PaginatedResponse[UserAggregrate]:

        filters = []

        if query.role is not None:
            filters.append(
                User.role == query.role
            )

        if query.level is not None:
            filters.append(
                User.level == query.level
            )

        if query.is_active is not None:
            filters.append(
                User.is_active == query.is_active
            )

        if query.search is not None and query.search.strip():
            search_term = f"%{query.search.strip()}%"

            filters.append(
                User.username.ilike(search_term),
            )

        count_stmt = (
            select(func.count())
            .select_from(User)
            .where(*filters)
        )

        total = await self.session.scalar(count_stmt)

        sort_columns = {
            "name": User.username,
            "level": User.level,
            "created_at": User.created_at,
            "updated_at": User.updated_at,
        }

        sort_column = sort_columns[query.sort_by]

        if query.sort_order == "asc":

            ordering = asc(sort_column)
        else:
            ordering = desc(sort_column)

        offset = (query.page - 1) * query.limit

        stmt = (
            select(User)
            .where(*filters)
            .order_by(ordering, User.created_at)
            .offset(offset)
            .limit(limit=query.limit)
        )

        result = await self.session.execute(stmt)

        users = result.scalars().all()

        return PaginatedResponse(
            items=[
                UserMapper.to_domain(user)
                for user in users
            ],
            total=total or 0,
            page=query.page,
            limit=query.limit
        )
 
    async def add(
        self,
        aggregate: UserAggregrate,
    ) -> UserAggregrate:

        user = UserMapper.to_model(aggregate)
        self.session.add(user)
        await self.session.flush()

        return UserMapper.to_domain(user)
    
    async def update(self, aggregate: UserAggregrate) -> UserAggregrate:

        user = UserMapper.to_model(aggregate=aggregate)
        updated_user = await self.session.merge(user)
        await self.session.flush()

        return UserMapper.to_domain(updated_user)

    async def delete(
        self,
        user_id: str,
    ) -> None:

        stmt = delete(User).where(User.id == user_id)
        await self.session.execute(stmt)
        await self.session.flush()
