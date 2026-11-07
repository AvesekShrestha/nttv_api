from dataclasses import dataclass
from pydantic import BaseModel

class TicketCompletedEvent(BaseModel):
    ticket_id: str
    user_id : str

