from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ticket.application.ticket.dto.activity_response_dto import TicketActivityResponseDTO

class TicketResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    priority: str
    status: str
    category_id: str
    created_by: str

    current_assignment_id: str | None = None

    activities: list[TicketActivityResponseDTO] = []

    created_at: datetime | None = None
    updated_at: datetime | None = None
    resolved_at: datetime | None = None
