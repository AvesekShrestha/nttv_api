from abc import ABC, abstractmethod
from datetime import date
from analytics.application.dashboard.dto.dashboard_dto import (
    DashboardOverviewResponseDTO,
    AgentDashboardOverviewResponseDTO,
)
from analytics.application.ticket_analytics.dto.ticket_analytics_query_dto import (
    TicketAnalyticsQueryDTO,
)


class IDashboardService(ABC):
    @abstractmethod
    async def get_admin_overview(
        self,
        query: TicketAnalyticsQueryDTO,
    ) -> DashboardOverviewResponseDTO:
        pass

    @abstractmethod
    async def get_agent_overview(
        self,
        agent_id: str,
        metric_date: date | None = None,
    ) -> AgentDashboardOverviewResponseDTO:
        pass
