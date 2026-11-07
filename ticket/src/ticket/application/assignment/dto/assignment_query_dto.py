from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AssignmentQueryDTO(BaseModel):

    model_config = ConfigDict(extra="forbid")

    ticket_id: str | None = None
    status: str | None = None

    acknowledgment_sla_breached: bool | None = None
    resolution_sla_breached: bool | None = None

    acknowledgment_sla_breached_recorded: bool | None = None
    resolution_sla_breached_recorded: bool | None = None

    sort_by: Literal[
        "assigned_at",
        "created_at",
        "updated_at",
        "acknowledgment_deadline_at",
        "resolution_deadline_at",
    ] = "created_at"

    sort_order: Literal["asc", "desc"] = "desc"

    page: int = Field(default=1, ge=1)
    limit: int = Field(default=5, ge=1, le=5)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit
