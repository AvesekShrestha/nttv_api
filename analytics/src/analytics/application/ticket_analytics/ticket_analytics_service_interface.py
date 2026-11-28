from abc import ABC, abstractmethod
from datetime import datetime

from analytics.application.ticket_analytics.dto.ticket_analytics_query_dto import (
    TicketAnalyticsQueryDTO,
)
from analytics.application.ticket_analytics.dto.ticket_analytics_dto import (
    TicketAnalysisResponseDTO,
)
from analytics.domain.events.ticket_created_event import TicketCreatedEvent


class ITicketAnalyticsService(ABC):

    @abstractmethod
    async def save(
        self,
        event_id: str,
        occurred_at: datetime,
        payload: TicketCreatedEvent,
    ) -> None:
        pass

    @abstractmethod
    async def generate_analysis(
        self,
        query: TicketAnalyticsQueryDTO,
    ) -> TicketAnalysisResponseDTO:
        pass
