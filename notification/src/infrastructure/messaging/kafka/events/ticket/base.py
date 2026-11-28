from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class EventModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class TicketEventSubject(EventModel):
    id: str = Field(min_length=1)


TSubject = TypeVar("TSubject", bound=TicketEventSubject)
TData = TypeVar("TData", bound=EventModel)


class TicketEvent(EventModel, Generic[TSubject, TData]):
    event_id: str = Field(min_length=1)
    occurred_at: datetime
    subject: TSubject
    data: TData
