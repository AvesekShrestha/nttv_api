from typing import Literal

from src.infrastructure.messaging.kafka.events.ticket.base import TicketEvent


class TicketForwardedEvent(TicketEvent):
    event_type: Literal["ticket_forwarded"]
