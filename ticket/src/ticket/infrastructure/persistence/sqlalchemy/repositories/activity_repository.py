from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ticket.application.interfaces.activity_repository_interface import IActivityRepository

from ticket.domain.ticket.entity.ticket_activity_entity import TicketActivityEntity

from ticket.infrastructure.persistence.sqlalchemy.mappers.activity_mapper import TicketActivityMapper
from ticket.infrastructure.persistence.sqlalchemy.models.activities_model import TicketActivity


class ActivityRepository(IActivityRepository) : 

    def __init__(self, session : AsyncSession): 
        self.session = session

    async def get_by_id(self, activity_id: str) -> TicketActivityEntity | None:

        statement = select(TicketActivity).where(TicketActivity.id == activity_id)
        result = await self.session.execute(statement=statement)

        activity = result.scalar_one_or_none()

        if not activity: return None
        return TicketActivityMapper.to_entity(activity)

    async def get_all(self, page : int = 1, limit: int = 5) -> list[TicketActivityEntity]:

        offset = (page -1) * limit

        statement = select(TicketActivity).offset(offset=offset).limit(limit=limit).order_by(TicketActivity.created_at.desc())
        result = await self.session.execute(statement=statement)

        activities = result.scalars().all()

        return[
            TicketActivityMapper.to_entity(activity)
            for activity in activities
        ]

    async def add(self, activity: TicketActivityEntity) -> TicketActivityEntity:
        activity_model = TicketActivityMapper.to_model(activity)

        self.session.add(activity_model)
        await self.session.flush()

        return TicketActivityMapper.to_entity(activity_model)

    async def delete(self, activity_id: str) -> None:

        stmt = delete(TicketActivity).where(TicketActivity.id == activity_id)
        await self.session.execute(stmt)
        await self.session.flush()
