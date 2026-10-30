from pydantic import BaseModel, Field

from ticket.domain.ticket.ticket_priority import TicketPriority


class TicketCreateDTO(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )

    description: str = Field(
        min_length=1,
    )

    priority: str = Field(
        default=TicketPriority.MEDIUM.value,
    )

    category_id: str = Field(
        min_length=1,
        max_length=30,
    )
