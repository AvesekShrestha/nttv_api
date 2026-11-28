from datetime import datetime
from pydantic import BaseModel


class AgentScoreResponseDTO(BaseModel):
    id: str
    agent_id: str | None
    ticket_id: str
    source_event_id: str
    activity_type: str
    points: int
    occurred_at: datetime


class AgentScoreSummaryResponseDTO(BaseModel):
    agent_id: str
    total_points: int
    scores: list[AgentScoreResponseDTO]
