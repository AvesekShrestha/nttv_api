from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class TicketSubject(BaseModel):
    category_id: str
    priority: str
    level: str
    title: str


class EventRecipient(BaseModel):
    email: EmailStr


class TicketEvent(BaseModel):
    event_id: str
    event_type: str
    occurred_at: datetime
    recipients: list[EventRecipient] = Field(min_length=1)
    subject: TicketSubject
