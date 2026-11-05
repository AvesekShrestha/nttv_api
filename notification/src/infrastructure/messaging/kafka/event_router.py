
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from src.infrastructure.messaging.kafka.handlers.ticket import (
    ticket_created,
    ticket_assigned,
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
            raise ValueError(f"Duplicate handler registration: {key}")

        self._handlers[key] = handler

    async def dispatch(
        self,
        topic: str,
        payload: object,
    ) -> None:
        if not isinstance(payload, dict):
            raise ValueError("Event payload must be a JSON object")

        event_type = payload.get("event_type")

        if not isinstance(event_type, str) or not event_type:
            raise ValueError("Event must contain a non-empty event_type")

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
            payload.get("event_id"),
        )

        await handler(payload)


def create_event_router(ticket_topic: str) -> EventRouter:
    router = EventRouter()

    router.register(ticket_topic, "ticket_created", ticket_created.handle)
    router.register(ticket_topic, "ticket_assigned", ticket_assigned.handle)

    return router
