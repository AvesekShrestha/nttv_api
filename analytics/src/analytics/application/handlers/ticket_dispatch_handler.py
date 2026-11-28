from pydantic import ValidationError
from analytics.application.exceptions import MissingRequiredAttributeException
from analytics.application.interfaces import ticket_analytics_repository_interface
from analytics.application.shared.event_handler_interface import IEventHandler

from analytics.application.interfaces.ticket_activity_repository_interface import (
    ITicketActivityRepository,
)
from analytics.application.interfaces.ticket_analytics_repository_interface import (
    ITicketAnalyticsRepository,
)

from analytics.application.shared.id_generator_interface import IIdGenerator

from analytics.domain.events.kafka_event import KafkaEvent
from analytics.domain.events.ticket_dispatch_event import (
    TicketDispatchedEvent,
)

from analytics.domain.ticket_activity.entity.ticket_activity_entity import (
    TicketActivityEntity,
)
from analytics.domain.ticket_activity.ticket_activity import TicketActivityType
from analytics.domain.ticket_analytics.ticket_status import TicketStatus


class TicketDispatchedHandler(IEventHandler):
    def __init__(
        self,
        ticket_activity_repository: ITicketActivityRepository,
        ticket_analytics_repository: ITicketAnalyticsRepository,
        id_generator: IIdGenerator,
    ):
        self._ticket_activity_repository = ticket_activity_repository
        self._ticket_analytics_repository = ticket_analytics_repository
        self._id_generator = id_generator

    @property
    def event_type(self) -> str:
        return "ticket.dispatched"

    async def handle(self, event: KafkaEvent) -> None:

        try:
            payload = TicketDispatchedEvent.model_validate(event.data)
        except ValidationError as e:
            raise MissingRequiredAttributeException(
                f"Required attribute is missing or null in ticket.dispatched event: {e}"
            )

        existing = await self._ticket_activity_repository.get_by_source_event_id(
            event.id
        )

        if existing is not None:
            return

        ticket = await self._ticket_analytics_repository.get_by_id(
            ticket_id=payload.ticket_id
        )

        if ticket is None:
            raise ValueError(
                f"Ticket analytics not found for ticket: {payload.ticket_id}"
            )

        ticket.update_status(status=TicketStatus.ASSIGNED)

        await self._ticket_analytics_repository.save(ticket)

        activity = TicketActivityEntity.create(
            activity_id=self._id_generator.generate_random_id(),
            source_event_id=event.id,
            ticket_id=payload.ticket_id,
            assignment_id=payload.assignment_id,
            actor_id=None,
            agent_id=payload.responsible_agent_id,
            team_id=payload.team_id,
            activity_type=TicketActivityType.DISPATCHED.value,
            occurred_at=event.occurred_at,
        )

        await self._ticket_activity_repository.save(activity)

