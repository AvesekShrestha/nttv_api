from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy import QueuePool
from sqlalchemy.ext.asyncio import AsyncSession

from analytics.config.container import container
from analytics.infrastructure.persistence.sqlalchemy.database import get_session

from analytics.application.ticket_analytics.dto.ticket_analytics_query_dto import (
    TicketAnalyticsQueryDTO,
)
from analytics.application.ticket_analytics.dto.ticket_analytics_dto import (
    TicketAnalysisResponseDTO,
)
from analytics.application.performance_metric.dto.performance_metric_dto import (
    PerformanceMetricQueryDTO,
    PerformanceMetricSummaryResponseDTO,
)
from analytics.application.agent_score.dto.agent_score_dto import (
    AgentScoreSummaryResponseDTO,
)
from analytics.application.ticket_activity.dto.ticket_activity_dto import (
    TicketActivityResponseDTO,
)
from analytics.application.dashboard.dto.dashboard_dto import (
    DashboardOverviewResponseDTO,
    AgentDashboardOverviewResponseDTO,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/tickets", response_model=TicketAnalysisResponseDTO)
async def get_ticket_analytics(
    start_date: date | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="End date (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_session),
):
    query = TicketAnalyticsQueryDTO(start_date=start_date, end_date=end_date)
    container.session.override(session)
    service = container.ticket_analytics_service()
    return await service.generate_analysis(query)


@router.get("/performance", response_model=PerformanceMetricSummaryResponseDTO)
async def get_performance_metrics(
    query : PerformanceMetricQueryDTO = Query(),
    session: AsyncSession = Depends(get_session),
):
    container.session.override(session)
    service = container.performance_metric_service()
    return await service.get_metrics_summary(dimension_type=query.dimension_type, dimension_id=query.dimension_id)


@router.get("/agents/{agent_id}/scores", response_model=AgentScoreSummaryResponseDTO)
async def get_agent_scores(
    agent_id: str,
    session: AsyncSession = Depends(get_session),
):
    container.session.override(session)
    service = container.agent_score_service()
    return await service.get_scores_by_agent(agent_id)


@router.get(
    "/tickets/{ticket_id}/activities", response_model=list[TicketActivityResponseDTO]
)
async def get_ticket_activities(
    ticket_id: str,
    session: AsyncSession = Depends(get_session),
):
    container.session.override(session)
    service = container.ticket_activity_service()
    return await service.get_activities_by_ticket_id(ticket_id)


@router.get("/dashboard/admin/overview", response_model=DashboardOverviewResponseDTO)
async def get_admin_dashboard_overview(
    start_date: date | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="End date (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_session),
):
    query = TicketAnalyticsQueryDTO(start_date=start_date, end_date=end_date)
    container.session.override(session)
    service = container.dashboard_service()
    return await service.get_admin_overview(query)


@router.get(
    "/dashboard/agents/{agent_id}/overview",
    response_model=AgentDashboardOverviewResponseDTO,
)
async def get_agent_dashboard_overview(
    agent_id: str,
    metric_date: date | None = Query(None, description="Metric date (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_session),
):
    container.session.override(session)
    service = container.dashboard_service()
    return await service.get_agent_overview(agent_id=agent_id, metric_date=metric_date)
