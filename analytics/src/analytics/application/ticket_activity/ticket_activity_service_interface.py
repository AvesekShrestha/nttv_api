from abc import ABC, abstractmethod
from analytics.application.ticket_activity.dto.ticket_activity_dto import (
    TicketActivityResponseDTO,
)


class ITicketActivityService(ABC):
    @abstractmethod
    async def get_activities_by_ticket_id(
        self,
        ticket_id: str,
    ) -> list[TicketActivityResponseDTO]:
        pass
