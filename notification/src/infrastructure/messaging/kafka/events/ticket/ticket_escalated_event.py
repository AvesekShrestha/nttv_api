from typing import Literal

from pydantic import AwareDatetime, Field

from src.infrastructure.messaging.kafka.events.ticket.base import (
    EventModel,
)


class TicketEscalatedData(EventModel):
    ticket_id: str = Field(min_length=1)
    assignment_id: str = Field(min_length=1)


class TicketEscalatedEvent(EventModel):
    id: str = Field(min_length=1)
    key: str = Field(min_length=1)
    event_type: Literal["ticket.escalated"]
    occurred_at: AwareDatetime
    data: TicketEscalatedData
    published_at: AwareDatetime | None = None
