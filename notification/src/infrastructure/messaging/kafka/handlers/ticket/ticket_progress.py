import logging
from typing import Any

import httpx

from src.application.notification.notify_ticket_progress import (
    NotifyTicketProgress,
    TicketProgressEventType,
)
from src.infrastructure.clients.ticket_client import TicketClient
from src.infrastructure.identity.id_generator import IdGenerator
from src.infrastructure.messaging.kafka.events.ticket.ticket_acknowledge_event import (
    TicketAcknowledgeEvent,
)
from src.infrastructure.messaging.kafka.events.ticket.ticket_completed_event import (
    TicketCompletedEvent,
)
from src.infrastructure.persistence.sqlalchemy.database import SessionLocal
from src.infrastructure.persistence.sqlalchemy.repositories.inbox_repository import (
    InboxRepository,
)

logger = logging.getLogger(__name__)


class TicketProgressHandler:
    def __init__(
        self,
        *,
        http_client: httpx.AsyncClient,
        source_topic: str,
        event_type: TicketProgressEventType,
    ):
        self.ticket_client = TicketClient(http_client)
        self.source_topic = source_topic

        self.event_model: (
            type[TicketAcknowledgeEvent]
            | type[TicketCompletedEvent]
        )

        if event_type == "ticket.acknowledged":
            self.event_model = TicketAcknowledgeEvent

        elif event_type == "ticket.completed":
            self.event_model = TicketCompletedEvent

        else:
            raise ValueError(
                "Unsupported ticket progress event type"
            )

    async def __call__(self, payload: dict[str, Any]) -> None:
        event = self.event_model.model_validate(payload)

        async with SessionLocal() as session:
            repository = InboxRepository(
                session=session,
                id_generator=IdGenerator(),
            )

            use_case = NotifyTicketProgress(
                ticket_client=self.ticket_client,
                inbox_repository=repository,
            )

            saved = await use_case.execute(
                event_id=event.id,
                event_type=event.event_type,
                occurred_at=event.occurred_at,
                ticket_id=event.data.ticket_id,
                actor_user_id=event.data.user_id,
                source_topic=self.source_topic,
            )

        logger.info(
            "Ticket progress %s: "
            "event_id=%s event_type=%s topic=%s",
            "saved" if saved else "already processed",
            event.id,
            event.event_type,
            self.source_topic,
        )
