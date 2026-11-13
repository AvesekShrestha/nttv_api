from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ticket.domain.ticket.ticket_priority import TicketPriority
from ticket.domain.ticket.ticket_status import TicketStatus


class TicketQueryDTO(BaseModel):

    model_config = ConfigDict(extra="forbid")

    user_id: str | None = None

    assignment_role: Literal[
        "responsible",
        "backup",
        "all",
    ] = "all"

    ticket_id: str | None = None
    category_id: str | None = None
    created_by: str | None = None

    status: TicketStatus | None = None
    priority: TicketPriority | None = None

    search: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    acknowledgment_sla_breached: bool | None = None
    resolution_sla_breached: bool | None = None

    sort_by: Literal[
        "created_at",
        "updated_at",
        "priority",
        "status",
    ] = "created_at"

    sort_order: Literal[
        "asc",
        "desc",
    ] = "desc"

    page: int = Field(default=1, ge=1)
    limit: int = Field(default=5, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit
