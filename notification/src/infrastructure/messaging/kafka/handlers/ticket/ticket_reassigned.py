import logging
from typing import Any

import httpx

from src.application.notification.notify_ticket_reassigned import (
    NotifyTicketReassigned,
    ReassignmentEventType,
)
from src.infrastructure.clients.ticket_client import TicketClient
from src.infrastructure.identity.id_generator import IdGenerator
from src.infrastructure.messaging.kafka.events.ticket.ticket_escalated_event import (
    TicketEscalatedEvent,
)
from src.infrastructure.messaging.kafka.events.ticket.ticket_forwarded_event import (
    TicketForwardedEvent,
)
from src.infrastructure.persistence.sqlalchemy.database import SessionLocal
from src.infrastructure.persistence.sqlalchemy.repositories.inbox_repository import (
    InboxRepository,
)

logger = logging.getLogger(__name__)


class TicketReassignedHandler:
    def __init__(
        self,
        *,
        http_client: httpx.AsyncClient,
        source_topic: str,
        event_type: ReassignmentEventType,
    ):
        self.ticket_client = TicketClient(http_client)
        self.source_topic = source_topic

        self.event_model: (
            type[TicketForwardedEvent]
            | type[TicketEscalatedEvent]
        )

        if event_type == "ticket.forwarded":
            self.event_model = TicketForwardedEvent

        elif event_type == "ticket.escalated":
            self.event_model = TicketEscalatedEvent

        else:
            raise ValueError(
                "Unsupported reassignment event type"
            )

    async def __call__(self, payload: dict[str, Any]) -> None:
        event = self.event_model.model_validate(payload)

        async with SessionLocal() as session:
            repository = InboxRepository(
                session=session,
                id_generator=IdGenerator(),
            )

            use_case = NotifyTicketReassigned(
                ticket_client=self.ticket_client,
                inbox_repository=repository,
            )

            saved = await use_case.execute(
                event_id=event.id,
                event_type=event.event_type,
                occurred_at=event.occurred_at,
                ticket_id=event.data.ticket_id,
                assignment_id=event.data.assignment_id,
                source_topic=self.source_topic,
            )

        logger.info(
            "Reassignment notification %s: "
            "event_id=%s event_type=%s topic=%s",
            "saved" if saved else "already processed",
            event.id,
            event.event_type,
            self.source_topic,
        )
