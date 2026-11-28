from pydantic import BaseModel
from typing import Literal


class TicketCreatedEvent(BaseModel):
    ticket_id: str
    category_id: str
    priority: str
    created_by: str
