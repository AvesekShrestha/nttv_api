from pydantic import BaseModel, ConfigDict


class TicketReassignmentEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticket_id: str

    previous_assignment_id: str
    new_assignment_id: str

    actor_id: str

    previous_team_id: str | None = None
    previous_agent_id: str | None = None

    new_team_ids: list[str]
    new_agent_ids: list[str]
