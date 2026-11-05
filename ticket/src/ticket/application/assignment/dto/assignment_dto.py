from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel, Field

from ticket.domain.assignment.assignment_type import AssignmentType
from ticket.domain.assignment.assignment_status import AssignmentStatus



@dataclass(frozen=True)
class AgentRecipientResponseDTO:
    id: str
    agent_id: str
    can_claim: bool
    notified_at: datetime | None
    acknowledged_at: datetime | None
    claimed_at: datetime | None


@dataclass(frozen=True)
class TeamRecipientResponseDTO:
    id: str
    team_id: str
    agents: list[AgentRecipientResponseDTO]


@dataclass(frozen=True)
class AssignmentResponseDTO:
    id: str
    ticket_id: str
    assigned_by: str | None
    assignment_type: AssignmentType
    status: AssignmentStatus

    primary_agent_id: str | None
    responsible_agent_id: str | None

    team_recipients: list[TeamRecipientResponseDTO]

    assigned_at: datetime | None
    acknowledgment_deadline_at: datetime | None
    resolution_deadline_at: datetime | None

    acknowledgment_sla_breached_at: datetime | None
    resolution_sla_breached_at: datetime | None

    completed_at: datetime | None

    created_at: datetime | None
    updated_at: datetime | None
    
@dataclass(frozen=True)
class AgentRecipientCreateDTO:
    agent_id : str

@dataclass(frozen=True)
class TeamRecipientCreateDTO:
    team_id : str
    agents : list[AgentRecipientCreateDTO]

class TeamAssignmentDTO(BaseModel):
    team_id: str
    agent_ids: list[str] = Field(min_length=1)

class ReassignmentDTO(BaseModel):
    teams: list[TeamAssignmentDTO] = Field(min_length=1)
