from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TicketAcknowledgedEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticket_id: str
    assignment_id: str

    actor_id: str

    agent_id: str

    team_id: str | None

    assigned_at: datetime

    acknowledgment_sla_deadline: datetime
