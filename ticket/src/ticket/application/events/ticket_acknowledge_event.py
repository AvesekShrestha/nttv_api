from dataclasses import dataclass
from pydantic import BaseModel

class TicketAcknowledgeEvent(BaseModel):
    ticket_id: str
    user_id : str
