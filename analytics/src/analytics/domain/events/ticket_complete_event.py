from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TicketCompletedEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticket_id: str
    assignment_id: str

    actor_id: str
    agent_id: str
    team_id: str | None = None

    resolution_sla_deadline: datetime | None = None
