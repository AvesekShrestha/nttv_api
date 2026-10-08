from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.outbox.entity.outbox_event import OutboxEvent
from src.application.interfaces.outbox_repository_interface import IOutboxRepository
from src.infrastructure.persistence.sqlalchemy.mappers.outbox_mappers import OutboxEventMapper
from src.infrastructure.persistence.sqlalchemy.models.outbox_event_model import OutboxEventModel

class OutboxRepository(IOutboxRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, event: OutboxEvent) -> None:
        model = OutboxEventMapper.to_model(event)
        self.session.add(model)
        await self.session.flush()

    async def get_unpublished(
        self,
        limit: int = 50,
    ) -> list[OutboxEvent]:

        result = await self.session.execute(
            select(OutboxEventModel)
            .where(
                OutboxEventModel.published_at.is_(None)
            )
            .order_by(
                OutboxEventModel.occurred_at
            )
            .limit(limit)
        )

        models = result.scalars().all()

        return [
            OutboxEventMapper.to_domain(model)
            for model in models
        ]

    async def update(self, event: OutboxEvent) -> None:

        event_model = OutboxEventMapper.to_model(event)
        model = await self.session.merge(event_model)
        await self.session.flush()
