from analytics.domain.agent_score.entity.agent_score_entity import (
    AgentScoreEntity,
)

from analytics.infrastructure.persistence.sqlalchemy.models.agent_score_model import (
    AgentScoreModel,
)


class AgentScoreMapper:

    @staticmethod
    def to_model(
        entity: AgentScoreEntity,
    ) -> AgentScoreModel:

        return AgentScoreModel(
            id=entity.id,
            agent_id=entity.agent_id,
            ticket_id=entity.ticket_id,
            source_event_id=entity.source_event_id,
            activity_type=entity.activity_type,
            points=entity.points,
            occurred_at=entity.occurred_at,
        )

    @staticmethod
    def to_entity(
        model: AgentScoreModel,
    ) -> AgentScoreEntity:

        return AgentScoreEntity.create(
            score_id=model.id,
            agent_id=model.agent_id,
            ticket_id=model.ticket_id,
            source_event_id=model.source_event_id,
            activity_type=model.activity_type,
            points=model.points,
            occurred_at=model.occurred_at,
        )
