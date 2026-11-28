from analytics.domain.analytics_event.analytics_event_status import AnalyticsEventStatus
from analytics.infrastructure.persistence.sqlalchemy.models.analytics_event_model import (
    AnalyticsEventModel,
)

from analytics.domain.analytics_event.analytics_event_aggregate import (
    AnalyticsEventAggregate,
)


class AnalyticsEventMapper:

    @staticmethod
    def to_domain(
        model: AnalyticsEventModel,
    ) -> AnalyticsEventAggregate:

        return AnalyticsEventAggregate(
            id=model.id,
            event_id=model.event_id,
            event_type=model.event_type,
            payload=model.payload,
            status=AnalyticsEventStatus.from_string(model.status),
            attempts=model.attempts,
            last_error=model.last_error,
            next_retry_at=model.next_retry_at,
            created_at=model.created_at,
            processed_at=model.processed_at,
        )

    @staticmethod
    def to_model(
        entity: AnalyticsEventAggregate,
    ) -> AnalyticsEventModel:

        return AnalyticsEventModel(
            id=entity.id,
            event_id=entity.event_id,
            event_type=entity.event_type,
            payload=entity.payload,
            status=entity.status,
            attempts=entity.attempts,
            last_error=entity.last_error,
            next_retry_at=entity.next_retry_at,
            created_at=entity.created_at,
            processed_at=entity.processed_at,
        )
