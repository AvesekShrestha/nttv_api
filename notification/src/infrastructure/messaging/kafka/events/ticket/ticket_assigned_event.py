from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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
    event_type: Literal["ticket.assigned"]
    occurred_at: datetime
    subject: TicketAssignedSubject
    data: TicketAssignedData
