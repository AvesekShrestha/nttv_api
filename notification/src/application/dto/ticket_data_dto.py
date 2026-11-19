from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


NonEmptyStr = Annotated[str, Field(min_length=1)]


class TicketApiModel(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
    )


class TicketDetails(TicketApiModel):
    id: NonEmptyStr
    title: NonEmptyStr
    created_by: NonEmptyStr


class AssignmentAgent(TicketApiModel):
    agent_id: NonEmptyStr
    can_claim: bool


class AssignmentTeam(TicketApiModel):
    team_id: NonEmptyStr
    agents: list[AssignmentAgent]


class AssignmentDetails(TicketApiModel):
    id: NonEmptyStr
    ticket_id: NonEmptyStr
    primary_agent_id: NonEmptyStr | None
    responsible_agent_id: NonEmptyStr | None
    team_recipients: list[AssignmentTeam]
