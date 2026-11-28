from analytics.domain.performance_mertic.entity.performance_matric_entity import (
    PerformanceMetricEntity,
)
from analytics.infrastructure.persistence.sqlalchemy.models.performance_metric_model import (
    PerformanceMetricModel,
)


class PerformanceMetricMapper:
    @staticmethod
    def to_model(
        entity: PerformanceMetricEntity,
    ) -> PerformanceMetricModel:

        return PerformanceMetricModel(
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

    @staticmethod
    def to_entity(
        model: PerformanceMetricModel,
    ) -> PerformanceMetricEntity:

        return PerformanceMetricEntity(
            metric_id=model.id,
            dimension_type=model.dimension_type,
            dimension_id=model.dimension_id,
            tickets_received=model.tickets_received,
            tickets_acknowledged=model.tickets_acknowledged,
            tickets_resolved=model.tickets_resolved,
            tickets_forwarded=model.tickets_forwarded,
            tickets_escalated=model.tickets_escalated,
            acknowledgment_sla_eligible=model.acknowledgment_sla_eligible,
            acknowledgment_sla_breached=model.acknowledgment_sla_breached,
            resolution_sla_eligible=model.resolution_sla_eligible,
            resolution_sla_breached=model.resolution_sla_breached,
            total_acknowledgment_seconds=model.total_acknowledgment_seconds,
            total_resolution_seconds=model.total_resolution_seconds,
        )
