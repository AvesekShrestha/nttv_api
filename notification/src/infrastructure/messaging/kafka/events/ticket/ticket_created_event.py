from typing import Literal

from pydantic import AwareDatetime, Field

from src.infrastructure.messaging.kafka.events.ticket.base import (
    EventModel,
)


class TicketCreatedData(EventModel):
    ticket_id: str = Field(min_length=1)


class TicketCreatedEvent(EventModel):
    id: str = Field(min_length=1)
    key: str = Field(min_length=1)
    event_type: Literal["ticket.created"]
    occurred_at: AwareDatetime
    data: TicketCreatedData
    published_at: AwareDatetime | None = None
