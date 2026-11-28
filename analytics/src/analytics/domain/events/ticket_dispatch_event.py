from pydantic import BaseModel


class TicketDispatchedEvent(BaseModel):

    ticket_id: str
    assignment_id: str

    assignment_type: str

    team_id: str | None

    primary_agent_id: str | None = None
    responsible_agent_id: str | None = None

    eligible_agent_ids: list[str]
