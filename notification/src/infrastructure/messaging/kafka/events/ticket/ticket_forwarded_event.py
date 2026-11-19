from typing import Literal

from pydantic import AwareDatetime, Field

from src.infrastructure.messaging.kafka.events.ticket.base import (
    EventModel,
)


class TicketForwardedData(EventModel):
    ticket_id: str = Field(min_length=1)
    assignment_id: str = Field(min_length=1)


class TicketForwardedEvent(EventModel):
    id: str = Field(min_length=1)
    key: str = Field(min_length=1)
    event_type: Literal["ticket.forwarded"]
    occurred_at: AwareDatetime
    data: TicketForwardedData
    published_at: AwareDatetime | None = None
