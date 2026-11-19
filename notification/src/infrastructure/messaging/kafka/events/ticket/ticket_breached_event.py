from typing import Literal

from pydantic import AwareDatetime, Field

from src.infrastructure.messaging.kafka.events.ticket.base import (
    EventModel,
)


class TicketBreachedData(EventModel):
    ticket_id: str = Field(min_length=1)
    assignment_id: str = Field(min_length=1)


class TicketBreachedEvent(EventModel):
    id: str = Field(min_length=1)
    key: str = Field(min_length=1)
    event_type: Literal["ticket.breached"]
    occurred_at: AwareDatetime
    data: TicketBreachedData
    published_at: AwareDatetime | None = None
