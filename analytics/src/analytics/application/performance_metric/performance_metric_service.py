from analytics.application.performance_metric.dto.performance_metric_dto import (
    PerformanceMetricSummaryResponseDTO,
    PerformanceMetricResponseDTO,
)
from analytics.application.performance_metric.performance_metric_service_interface import (
    IPerformanceMetricService,
)
from analytics.application.interfaces.performance_metric_repository_interface import (
    IPerformanceMetricRepository,
)


class PerformanceMetricService(IPerformanceMetricService):

    def __init__(
        self,
        performance_metric_repository: IPerformanceMetricRepository,
    ):
        self._performance_metric_repository = performance_metric_repository

    async def get_metric(
        self,
        dimension_type: str,
        dimension_id: str,
    ) -> PerformanceMetricResponseDTO | None:

        entity = await self._performance_metric_repository.get_by_dimension(
            dimension_type=dimension_type,
            dimension_id=dimension_id,
        )

        if entity is None:
            return None

        return PerformanceMetricResponseDTO(
            id=entity.id,
            dimension_type=entity.dimension_type,
            dimension_id=entity.dimension_id,
            tickets_received=entity.tickets_received,
            tickets_acknowledged=entity.tickets_acknowledged,
            tickets_resolved=entity.tickets_resolved,
            tickets_forwarded=entity.tickets_forwarded,
            tickets_escalated=entity.tickets_escalated,
            acknowledgment_sla_eligible=entity.acknowledgment_sla_eligible,
            acknowledgment_sla_breached=entity.acknowledgment_sla_breached,
            resolution_sla_eligible=entity.resolution_sla_eligible,
            resolution_sla_breached=entity.resolution_sla_breached,
            total_acknowledgment_seconds=entity.total_acknowledgment_seconds,
            total_resolution_seconds=entity.total_resolution_seconds,
        )

    async def get_metrics_summary(
        self,
        dimension_type: str,
        dimension_id: str,
    ) -> PerformanceMetricSummaryResponseDTO:

        entity = await self._performance_metric_repository.get_by_dimension(
            dimension_type=dimension_type,
            dimension_id=dimension_id,
        )

        if entity is None:
            return PerformanceMetricSummaryResponseDTO(
                dimension_type=dimension_type,
                dimension_id=dimension_id,
                total_tickets_received=0,
                total_tickets_acknowledged=0,
                total_tickets_resolved=0,
                total_tickets_forwarded=0,
                total_tickets_escalated=0,
                total_acknowledgment_sla_eligible=0,
                total_acknowledgment_sla_breached=0,
                total_resolution_sla_eligible=0,
                total_resolution_sla_breached=0,
                avg_acknowledgment_seconds=0.0,
                avg_resolution_seconds=0.0,
            )

        avg_ack_sec = (
            entity.total_acknowledgment_seconds
            / entity.tickets_acknowledged
            if entity.tickets_acknowledged > 0
            else 0.0
        )

        avg_res_sec = (
            entity.total_resolution_seconds
            / entity.tickets_resolved
            if entity.tickets_resolved > 0
            else 0.0
        )

        return PerformanceMetricSummaryResponseDTO(
            dimension_type=entity.dimension_type,
            dimension_id=entity.dimension_id,
            total_tickets_received=entity.tickets_received,
            total_tickets_acknowledged=entity.tickets_acknowledged,
            total_tickets_resolved=entity.tickets_resolved,
            total_tickets_forwarded=entity.tickets_forwarded,
            total_tickets_escalated=entity.tickets_escalated,
            total_acknowledgment_sla_eligible=entity.acknowledgment_sla_eligible,
            total_acknowledgment_sla_breached=entity.acknowledgment_sla_breached,
            total_resolution_sla_eligible=entity.resolution_sla_eligible,
            total_resolution_sla_breached=entity.resolution_sla_breached,
            avg_acknowledgment_seconds=round(avg_ack_sec, 2),
            avg_resolution_seconds=round(avg_res_sec, 2),
        )
