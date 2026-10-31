
from typing import Literal

from pydantic import EmailStr, Field

from src.infrastructure.messaging.kafka.events.ticket.base import (
    EventModel,
    TicketEvent,
    TicketEventSubject,
)


class TicketCreatedSubject(TicketEventSubject):
    type: Literal["ticket"]


class TicketCreatedRecipient(EventModel):
    email: EmailStr


class TicketCreatedData(EventModel):
    category: str = Field(min_length=1)
    priority: str = Field(min_length=1)
    level: str = Field(min_length=1)
    title: str = Field(min_length=1)
    recipients: list[TicketCreatedRecipient] = Field(min_length=1)


class TicketCreatedEvent(
    TicketEvent[TicketCreatedSubject, TicketCreatedData]
):
    event_type: Literal["ticket.created"]
