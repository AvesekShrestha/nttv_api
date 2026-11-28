from analytics.infrastructure.persistence.sqlalchemy.models.ticket_analytics_model import (
    TicketAnalyticsModel,
)
from analytics.domain.ticket_analytics.entity.ticket_analytics_entity import TicketAnalyticsEntity

class TicketAnalyticsMapper:

    @staticmethod
    def to_model(entity: TicketAnalyticsEntity) -> TicketAnalyticsModel:
        return TicketAnalyticsModel(
            ticket_id=entity.id,
            category_id=entity.category_id,
            created_by=entity.created_by,
            priority=entity.priority,
            current_status=entity.current_status,
            created_at=entity.created_at,
            resolved_at=entity.resolved_at,
            resolution_duration_seconds=entity.resolution_duration_seconds,
        )

    @staticmethod
    def to_domain(model: TicketAnalyticsModel) -> TicketAnalyticsEntity:
        return TicketAnalyticsEntity(
            ticket_id=model.ticket_id,
            category_id=model.category_id,
            created_by=model.created_by,
            priority=model.priority,
            current_status=model.current_status,
            created_at=model.created_at,
            resolved_at=model.resolved_at,
            resolution_duration_seconds=model.resolution_duration_seconds,
        )
