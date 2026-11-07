from dataclasses import dataclass
from pydantic import BaseModel

class TicketDispatchedEvent(BaseModel):
    ticket_id: str
    assignment_id : str

