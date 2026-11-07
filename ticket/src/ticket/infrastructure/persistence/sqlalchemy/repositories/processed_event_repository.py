from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ticket.application.interfaces.processed_event_repository_interface import (
    IProcessedEventRepository
)
from ticket.domain.event.entity.processed_event_entity import ProcessedEventEntity

from ticket.infrastructure.persistence.sqlalchemy.models.processed_event_model import (
    ProcessedEvent
)


class ProcessedEventRepository(IProcessedEventRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def exists(
        self,
        event_id: str,
    ) -> bool:

        statement = select(ProcessedEvent.event_id).where(
            ProcessedEvent.event_id == event_id,
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none() is not None

    async def add(
        self,
        event: ProcessedEventEntity
    ) -> None:

        model = ProcessedEvent(
            event_id=event.event_id,
            event_type=event.event_type,
            processed_at=event.processed_at
        )

        self.session.add(model)
