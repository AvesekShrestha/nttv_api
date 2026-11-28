import logging
from collections.abc import Awaitable, Callable
from typing import Any

import httpx

from src.infrastructure.messaging.kafka.handlers.auth import (
    otp_resend,
    user_created,
)
from src.infrastructure.messaging.kafka.handlers.ticket import (
    ticket_assigned,
)
from src.infrastructure.messaging.kafka.handlers.ticket.ticket_breached import (
    TicketBreachedHandler,
)
from src.infrastructure.messaging.kafka.handlers.ticket.ticket_created import (
    TicketCreatedHandler,
)
from src.infrastructure.messaging.kafka.handlers.ticket.ticket_dispatched import (
    TicketDispatchedHandler,
)
from src.infrastructure.messaging.kafka.handlers.ticket.ticket_progress import (
    TicketProgressHandler,
)
from src.infrastructure.messaging.kafka.handlers.ticket.ticket_reassigned import (
    TicketReassignedHandler,
)

logger = logging.getLogger(__name__)

EventPayload = dict[str, Any]
EventHandler = Callable[[EventPayload], Awaitable[None]]


class UnknownEventHandlerError(Exception):
    """Raised when no handler is registered for a topic and event type."""


class EventRouter:
    def __init__(self) -> None:
        self._handlers: dict[tuple[str, str], EventHandler] = {}

    def register(
        self,
        topic: str,
        event_type: str,
        handler: EventHandler,
    ) -> None:
        key = (topic, event_type)

        if key in self._handlers:
            raise ValueError(
                f"Duplicate handler registration: {key}"
            )

        self._handlers[key] = handler

    async def dispatch(
        self,
        topic: str,
        payload: object,
    ) -> None:
        if not isinstance(payload, dict):
            raise ValueError(
                "Event payload must be a JSON object"
            )

        event_type = payload.get("event_type")

        if not isinstance(event_type, str) or not event_type:
            raise ValueError(
                "Event must contain a non-empty event_type"
            )

        handler = self._handlers.get((topic, event_type))

        if handler is None:
            raise UnknownEventHandlerError(
                f"No handler registered for topic={topic!r}, "
                f"event_type={event_type!r}"
            )

        logger.info(
            "Dispatching topic=%s event_type=%s event_id=%s",
            topic,
            event_type,
            payload.get("event_id") or payload.get("id"),
        )

        await handler(payload)


def create_event_router(
    ticket_topic: str,
    auth_topic: str,
    ticket_http_client: httpx.AsyncClient,
) -> EventRouter:
    router = EventRouter()

    router.register(
        ticket_topic,
        "ticket.created",
        TicketCreatedHandler(
            http_client=ticket_http_client,
            source_topic=ticket_topic,
        ),
    )

    router.register(
        ticket_topic,
        "ticket.assigned",
        ticket_assigned.handle,
    )

    router.register(
        ticket_topic,
        "ticket.dispatched",
        TicketDispatchedHandler(
            http_client=ticket_http_client,
            source_topic=ticket_topic,
        ),
    )

    router.register(
        ticket_topic,
        "ticket.forwarded",
        TicketReassignedHandler(
            http_client=ticket_http_client,
            source_topic=ticket_topic,
            event_type="ticket.forwarded",
        ),
    )

    router.register(
        ticket_topic,
        "ticket.escalated",
        TicketReassignedHandler(
            http_client=ticket_http_client,
            source_topic=ticket_topic,
            event_type="ticket.escalated",
        ),
    )

    router.register(
        ticket_topic,
        "ticket.acknowledged",
        TicketProgressHandler(
            http_client=ticket_http_client,
            source_topic=ticket_topic,
            event_type="ticket.acknowledged",
        ),
    )

    router.register(
        ticket_topic,
        "ticket.completed",
        TicketProgressHandler(
            http_client=ticket_http_client,
            source_topic=ticket_topic,
            event_type="ticket.completed",
        ),
    )

    router.register(
        ticket_topic,
        "ticket.breached",
        TicketBreachedHandler(
            http_client=ticket_http_client,
            source_topic=ticket_topic,
        ),
    )

    router.register(
        auth_topic,
        "user.created",
        user_created.handle,
    )

    router.register(
        auth_topic,
        "otp.resend",
        otp_resend.handle,
    )

    return router
