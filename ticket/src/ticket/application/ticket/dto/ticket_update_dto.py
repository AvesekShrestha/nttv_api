from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ticket.domain.ticket.ticket_priority import TicketPriority
from ticket.domain.ticket.ticket_status import TicketStatus


class TicketUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    priority: str
    status: str
    category_id: str
    created_by: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    resolved_at: datetime | None = None
