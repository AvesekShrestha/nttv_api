from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TicketActivityResponseDTO(BaseModel):
    id: str
    source_event_id: str
    ticket_id: str
    assignment_id: Optional[str]
    actor_id: Optional[str]
    agent_id: Optional[str]
    team_id: Optional[str]
    activity_type: str
    occurred_at: datetime
