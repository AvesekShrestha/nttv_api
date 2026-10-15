
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.infrastructure.messaging.kafka.handlers.ticket.shared import (
    process_notifications,
)


class EventModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class TicketCreatedSubject(EventModel):
    type: Literal["ticket"]
    id: str = Field(min_length=1)


class TicketCreatedRecipient(EventModel):
    email: EmailStr


class TicketCreatedData(EventModel):
    category: str = Field(min_length=1)
    priority: str = Field(min_length=1)
    level: str = Field(min_length=1)
    title: str = Field(min_length=1)
    recipients: list[TicketCreatedRecipient] = Field(min_length=1)


class TicketCreatedEvent(EventModel):
    event_id: str = Field(min_length=1)
    event_type: Literal["ticket_created"]
    occurred_at: datetime
    subject: TicketCreatedSubject
    data: TicketCreatedData


def build_message(event: TicketCreatedEvent) -> str:
    return (
        "A new ticket has been created.\n\n"
        f"Ticket ID: {event.subject.id}\n"
        f"Title: {event.data.title}\n"
        f"Category: {event.data.category}\n"
        f"Priority: {event.data.priority}\n"
        f"Support level: {event.data.level}\n"
        f"Created at: {event.occurred_at.isoformat()}"
    )


async def handle(payload: dict[str, Any]) -> None:
    event = TicketCreatedEvent.model_validate(payload)

    await process_notifications(
        event_id=event.event_id,
        event_type=event.event_type,
        recipients=[
            str(recipient.email)
            for recipient in event.data.recipients
        ],
        subject=f"[New Ticket] {event.data.title}",
        message=build_message(event),
    )
