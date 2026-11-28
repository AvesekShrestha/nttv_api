from typing import Literal

from pydantic import AwareDatetime, Field

from src.infrastructure.messaging.kafka.events.ticket.base import (
    EventModel,
)


class TicketDispatchedData(EventModel):
    ticket_id: str = Field(min_length=1)
    assignment_id: str = Field(min_length=1)


class TicketDispatchedEvent(EventModel):
    id: str = Field(min_length=1)
    key: str = Field(min_length=1)
    event_type: Literal["ticket.dispatched"]
    occurred_at: AwareDatetime
    data: TicketDispatchedData
    published_at: AwareDatetime | None = None
