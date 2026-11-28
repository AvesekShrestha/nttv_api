from pydantic import BaseModel, ValidationError

from analytics.application.shared.event_handler_interface import IEventHandler
from analytics.application.interfaces.ticket_analytics_repository_interface import (
    ITicketAnalyticsRepository,
)
from analytics.domain.events.kafka_event import KafkaEvent
from analytics.domain.events.ticket_created_event import TicketCreatedEvent

from analytics.domain.ticket_analytics.entity.ticket_analytics_entity import (
    TicketAnalyticsEntity,
)
from analytics.domain.ticket_analytics.ticket_status import TicketStatus
from analytics.application.exceptions import MissingRequiredAttributeException


class TicketCreatedHandler(IEventHandler):
    def __init__(
        self,
        ticket_analytics_repository: ITicketAnalyticsRepository,
    ):
        self._ticket_analytics_repository = ticket_analytics_repository

    @property
    def event_type(self) -> str:
        return "ticket.created"

    async def handle(self, event: KafkaEvent) -> None:

        try:
            payload = TicketCreatedEvent.model_validate(event.data)
        except ValidationError as e:
            raise MissingRequiredAttributeException(
                f"Required attribute is missing or null in ticket.created event: {e}"
            )

        existing = await self._ticket_analytics_repository.get_by_id(payload.ticket_id)
        if existing is not None:
            return

        entity = TicketAnalyticsEntity.create(
            ticket_id=payload.ticket_id,
            category_id=payload.category_id,
            created_by=payload.created_by,
            priority=payload.priority,
            current_status=TicketStatus.NEW.value,
            created_at=event.occurred_at,
        )

        await self._ticket_analytics_repository.save(entity)
