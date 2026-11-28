from abc import ABC, abstractmethod

from analytics.application.ticket_analytics.dto.ticket_analytics_query_dto import TicketAnalyticsQueryDTO
from analytics.application.ticket_analytics.dto.ticket_analytics_dto import TicketDistributionDTO, TicketSummaryDTO, TicketTrendDTO
from analytics.domain.ticket_analytics.entity.ticket_analytics_entity import (
    TicketAnalyticsEntity,
)


class ITicketAnalyticsRepository(ABC):

    @abstractmethod
    async def save(self, entity: TicketAnalyticsEntity) -> None:
        pass

    @abstractmethod
    async def get_by_id(
        self,
        ticket_id: str,
    ) -> TicketAnalyticsEntity | None:
        pass

    @abstractmethod
    async def exists(self, ticket_id: str) -> bool:
        pass

    @abstractmethod
    async def get_summary(
        self,
        query: TicketAnalyticsQueryDTO,
    ) -> TicketSummaryDTO:
        pass

    @abstractmethod
    async def get_distribution(
        self,
        query: TicketAnalyticsQueryDTO,
    ) -> TicketDistributionDTO:
        pass

    @abstractmethod
    async def get_trends(
        self,
        query: TicketAnalyticsQueryDTO,
    ) -> list[TicketTrendDTO]:
        pass
