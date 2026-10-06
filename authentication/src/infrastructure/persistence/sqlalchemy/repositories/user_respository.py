from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import false, select, delete, update
from sqlalchemy.orm import session

from src.domain.users.user_role import UserRole
from src.application.interfaces.user_repository_interface import IUserRepository
from src.infrastructure.persistence.sqlalchemy.models.user_model import User
from src.infrastructure.persistence.sqlalchemy.mappers.user_infrastructure_mapper import UserMapper
from src.domain.users.user_aggregrate import UserAggregrate


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
    ) -> list[UserAggregrate]:

        stmt = select(User)
        result = await self.session.execute(stmt)

        users = result.scalars().all()

        return [
            UserMapper.to_domain(user)
            for user in users
        ]
 
    async def add(
        self,
        aggregate: UserAggregrate,
    ) -> UserAggregrate:

        user = UserMapper.to_model(aggregate)
        self.session.add(user)
        await self.session.commit()

        return UserMapper.to_domain(user)
    
    async def update(self, aggregate: UserAggregrate) -> UserAggregrate:

        user = UserMapper.to_model(aggregate=aggregate)
        updated_user = await self.session.merge(user)
        await self.session.commit()

        return UserMapper.to_domain(updated_user)

    async def delete(
        self,
        user_id: str,
    ) -> None:

        stmt = delete(User).where(User.id == user_id)
        await self.session.execute(stmt)
