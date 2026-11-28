from datetime import date
from pydantic import BaseModel


class DashboardOverviewResponseDTO(BaseModel):
    total_tickets: int
    resolved_tickets: int
    unresolved_tickets: int
    resolution_rate: float
    average_resolution_seconds: float
    by_status: dict[str, int]
    by_priority: dict[str, int]
    by_category: dict[str, int]


class AgentDashboardOverviewResponseDTO(BaseModel):
    agent_id: str
    total_points: int
    assigned_or_held_tickets: int
    resolved_tickets: int
    performance_summary: dict
