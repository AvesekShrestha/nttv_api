from pydantic import BaseModel, Field


class BulkTeamRequestDTO(BaseModel):
    team_ids: list[str] = Field(min_length=1)
