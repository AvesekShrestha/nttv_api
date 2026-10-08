from src.domain.outbox.entity.outbox_event import OutboxEvent
from src.infrastructure.persistence.sqlalchemy.models.outbox_event_model import OutboxEventModel


class OutboxEventMapper:

    @staticmethod
    def to_model(event: OutboxEvent) -> OutboxEventModel:
        return OutboxEventModel(
            id=event.id,
            event_type=event.event_type,
            occurred_at=event.occurred_at,
            data=event.data,
            published_at=event.published_at,
        )

    @staticmethod
    def to_domain(model: OutboxEventModel) -> OutboxEvent:
        return OutboxEvent(
            _id=model.id,
            _event_type=model.event_type,
            _occurred_at=model.occurred_at,
            _data=model.data,
            _published_at=model.published_at,
        )
