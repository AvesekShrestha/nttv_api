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


class TicketAssignedSubject(EventModel):
    type: Literal["ticket"]
    id: str = Field(min_length=1)


class TicketAssignedRecipient(EventModel):
    email: EmailStr


class TicketAssignedData(EventModel):
    team_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    assignment_type: str = Field(min_length=1)
    recipients: list[TicketAssignedRecipient] = Field(min_length=1)


class TicketAssignedEvent(EventModel):
    event_id: str = Field(min_length=1)
    event_type: Literal["ticket_assigned"]
    occurred_at: datetime
    subject: TicketAssignedSubject
    data: TicketAssignedData


def build_message(event: TicketAssignedEvent) -> str:
    return (
        "A ticket has been assigned.\n\n"
        f"Ticket ID: {event.subject.id}\n"
        f"Assignment type: {event.data.assignment_type}\n"
        f"Assigned team ID: {event.data.team_id}\n"
        f"Assigned agent ID: {event.data.agent_id}\n"
        f"Assigned at: {event.occurred_at.isoformat()}"
    )


async def handle(payload: dict[str, Any]) -> None:
    event = TicketAssignedEvent.model_validate(payload)

    await process_notifications(
        event_id=event.event_id,
        event_type=event.event_type,
        recipients=[
            str(recipient.email)
            for recipient in event.data.recipients
        ],
        subject=f"[Ticket Assigned] {event.subject.id}",
        message=build_message(event),
    )
