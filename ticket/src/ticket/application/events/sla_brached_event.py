from dataclasses import dataclass
from pydantic import BaseModel

class SLABreachedEvent(BaseModel):
    assignment_id : str
    ticket_id: str
