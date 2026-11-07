from dataclasses import dataclass
from pydantic import BaseModel

class TicketEscalatedEvent(BaseModel):
    ticket_id: str
    assignment_id : str

