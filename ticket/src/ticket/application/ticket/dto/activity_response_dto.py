from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TicketActivityResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ticket_id: str
    activity_type: str
    actor_id: str | None
    created_at: datetime | None = None
