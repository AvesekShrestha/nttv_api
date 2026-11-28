from datetime import date
from analytics.application.dashboard.dto.dashboard_dto import (
    DashboardOverviewResponseDTO,
    AgentDashboardOverviewResponseDTO,
)
from analytics.application.dashboard.dashboard_service_interface import (
    IDashboardService,
)
from analytics.application.ticket_analytics.dto.ticket_analytics_query_dto import (
    TicketAnalyticsQueryDTO,
)
from analytics.application.interfaces.ticket_analytics_repository_interface import (
    ITicketAnalyticsRepository,
)
from analytics.application.interfaces.agent_score_repository_interface import (
    IAgentScoreRepository,
)
from analytics.application.interfaces.performance_metric_repository_interface import (
    IPerformanceMetricRepository,
)


class DashboardService(IDashboardService):
    def __init__(
        self,
        ticket_analytics_repository: ITicketAnalyticsRepository,
        agent_score_repository: IAgentScoreRepository,
        performance_metric_repository: IPerformanceMetricRepository,
    ):
        self._ticket_analytics_repository = ticket_analytics_repository
        self._agent_score_repository = agent_score_repository
        self._performance_metric_repository = performance_metric_repository

    async def get_admin_overview(
        self,
        query: TicketAnalyticsQueryDTO,
    ) -> DashboardOverviewResponseDTO:
        summary = await self._ticket_analytics_repository.get_summary(query)
        distribution = await self._ticket_analytics_repository.get_distribution(query)

        return DashboardOverviewResponseDTO(
            total_tickets=summary.total_tickets,
            resolved_tickets=summary.resolved_tickets,
            unresolved_tickets=summary.unresolved_tickets,
            resolution_rate=summary.resolution_rate,
            average_resolution_seconds=summary.average_resolution_seconds,
            by_status=distribution.by_status,
            by_priority=distribution.by_priority,
            by_category=distribution.by_category,
        )

    async def get_agent_overview(
        self,
        agent_id: str,
        metric_date: date | None = None,
    ) -> AgentDashboardOverviewResponseDTO:
        total_points = await self._agent_score_repository.get_total_points_by_agent(
            agent_id
        )

        target_date = metric_date or date.today()
        metric = await self._performance_metric_repository.get_by_dimension(
            dimension_type="AGENT",
            dimension_id=agent_id,
            metric_date=target_date,
        )

        resolved_tickets = metric.tickets_resolved if metric else 0
        received_tickets = metric.tickets_received if metric else 0

        performance_summary = {}
        if metric:
            performance_summary = {
                "tickets_received": metric.tickets_received,
                "tickets_acknowledged": metric.tickets_acknowledged,
                "tickets_resolved": metric.tickets_resolved,
                "tickets_forwarded": metric.tickets_forwarded,
                "tickets_escalated": metric.tickets_escalated,
                "acknowledgment_sla_eligible": metric.acknowledgment_sla_eligible,
                "acknowledgment_sla_breached": metric.acknowledgment_sla_breached,
                "resolution_sla_eligible": metric.resolution_sla_eligible,
                "resolution_sla_breached": metric.resolution_sla_breached,
            }

        return AgentDashboardOverviewResponseDTO(
            agent_id=agent_id,
            total_points=total_points,
            assigned_or_held_tickets=received_tickets,
            resolved_tickets=resolved_tickets,
            performance_summary=performance_summary,
        )
