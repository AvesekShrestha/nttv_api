from dataclasses import dataclass
from pydantic import BaseModel

class TicketCreatedEvent(BaseModel):
    ticket_id: str

