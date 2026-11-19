import logging
from typing import Any

import httpx

from src.application.notification.notify_ticket_breached import (
    NotifyTicketBreached,
)
from src.infrastructure.clients.ticket_client import TicketClient
from src.infrastructure.identity.id_generator import IdGenerator
from src.infrastructure.messaging.kafka.events.ticket.ticket_breached_event import (
    TicketBreachedEvent,
)
from src.infrastructure.persistence.sqlalchemy.database import SessionLocal
from src.infrastructure.persistence.sqlalchemy.repositories.inbox_repository import (
    InboxRepository,
)

logger = logging.getLogger(__name__)


class TicketBreachedHandler:
    def __init__(
        self,
        *,
        http_client: httpx.AsyncClient,
        source_topic: str,
    ):
        self.ticket_client = TicketClient(http_client)
        self.source_topic = source_topic

    async def __call__(self, payload: dict[str, Any]) -> None:
        event = TicketBreachedEvent.model_validate(payload)

        async with SessionLocal() as session:
            repository = InboxRepository(
                session=session,
                id_generator=IdGenerator(),
            )

            use_case = NotifyTicketBreached(
                ticket_client=self.ticket_client,
                inbox_repository=repository,
            )

            saved = await use_case.execute(
                event_id=event.id,
                occurred_at=event.occurred_at,
                ticket_id=event.data.ticket_id,
                assignment_id=event.data.assignment_id,
                source_topic=self.source_topic,
            )

        logger.info(
            "Ticket breach %s: event_id=%s topic=%s",
            "saved" if saved else "already processed",
            event.id,
            self.source_topic,
        )
