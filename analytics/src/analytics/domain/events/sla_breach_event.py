from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class SLABreachedEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticket_id: str
    assignment_id: str

    sla_type: Literal["ACKNOWLEDGMENT", "RESOLUTION"]

    agent_id: str | None = None
    team_id: str | None = None

    deadline_at: datetime | None
