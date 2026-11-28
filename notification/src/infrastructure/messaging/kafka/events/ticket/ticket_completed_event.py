from typing import Literal

from pydantic import AwareDatetime, Field

from src.infrastructure.messaging.kafka.events.ticket.base import (
    EventModel,
)


class TicketCompletedData(EventModel):
    ticket_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)


class TicketCompletedEvent(EventModel):
    id: str = Field(min_length=1)
    key: str = Field(min_length=1)
    event_type: Literal["ticket.completed"]
    occurred_at: AwareDatetime
    data: TicketCompletedData
    published_at: AwareDatetime | None = None
