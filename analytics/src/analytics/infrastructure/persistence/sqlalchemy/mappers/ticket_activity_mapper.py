from analytics.domain.ticket_activity.entity.ticket_activity_entity import (
    TicketActivityEntity,
)

from analytics.infrastructure.persistence.sqlalchemy.models.ticket_activity_model import (
    TicketActivityModel,
)

class TicketActivityMapper:

    @staticmethod
    def to_model(
        entity: TicketActivityEntity,
    ) -> TicketActivityModel:

        return TicketActivityModel(
            id=entity.id,
            source_event_id=entity.source_event_id,
            ticket_id=entity.ticket_id,
            assignment_id=entity.assignment_id,
            actor_id=entity.actor_id,
            agent_id=entity.agent_id,
            team_id=entity.team_id,
            activity_type=entity.activity_type,
            occurred_at=entity.occurred_at,
        )

    @staticmethod
    def to_entity(
        model: TicketActivityModel,
    ) -> TicketActivityEntity:

        return TicketActivityEntity.create(
            activity_id=model.id,
            source_event_id=model.source_event_id,
            ticket_id=model.ticket_id,
            assignment_id=model.assignment_id,
            actor_id=model.actor_id,
            agent_id=model.agent_id,
            team_id=model.team_id,
            activity_type=model.activity_type,
            occurred_at=model.occurred_at,
        )
