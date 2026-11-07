from dataclasses import dataclass
from pydantic import BaseModel

class TicketForwardedEvent(BaseModel):
    ticket_id: str
    assignment_id : str

