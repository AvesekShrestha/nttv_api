from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from analytics.application.interfaces.ticket_activity_repository_interface import (
    ITicketActivityRepository,
)

from analytics.domain.ticket_activity.entity.ticket_activity_entity import TicketActivityEntity

from analytics.infrastructure.persistence.sqlalchemy.models.ticket_activity_model import TicketActivityModel
from analytics.infrastructure.persistence.sqlalchemy.mappers.ticket_activity_mapper import TicketActivityMapper


class TicketActivityRepository(ITicketActivityRepository):

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def save(
        self,
        activity: TicketActivityEntity,
    ) -> None:

        model = TicketActivityMapper.to_model(activity)

        await self._session.merge(model)
        await self._session.flush()

    async def get_by_source_event_id(
        self,
        source_event_id: str,
    ) -> TicketActivityEntity | None:

        stmt = select(TicketActivityModel).where(
            TicketActivityModel.source_event_id == source_event_id
        )

        result = await self._session.execute(stmt)

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return TicketActivityMapper.to_entity(model)

    async def get_by_ticket_id(
        self,
        ticket_id: str,
    ) -> list[TicketActivityEntity]:

        stmt = (
            select(TicketActivityModel)
            .where(
                TicketActivityModel.ticket_id == ticket_id
            )
            .order_by(
                TicketActivityModel.occurred_at.asc()
            )
        )

        result = await self._session.execute(stmt)

        models = result.scalars().all()

        return [
            TicketActivityMapper.to_entity(model)
            for model in models
        ]
