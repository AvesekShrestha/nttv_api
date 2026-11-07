from ticket.domain.assignment.entity.agent_recipient_entity import (
    AgentRecipientEntity,
)

from ticket.infrastructure.persistence.sqlalchemy.models.assignment_agent_recipient_model import (
    AssignmentAgentRecipient,
)

class AgentRecipientMapper:

    @staticmethod
    def to_model(
        aggregate: AgentRecipientEntity,
    ) -> AssignmentAgentRecipient:

        return AssignmentAgentRecipient(
            id=aggregate.id,
            team_recipient_id=aggregate.team_recipient_id,
            agent_id=aggregate.agent_id,
            can_claim=aggregate.can_claim,
            notified_at=aggregate.notified_at,
            acknowledged_at=aggregate.acknowledged_at,
            claimed_at=aggregate.claimed_at,
        )

    @staticmethod
    def to_domain(
        model: AssignmentAgentRecipient,
    ) -> AgentRecipientEntity:

        return AgentRecipientEntity(
            _id=model.id,
            _team_recipient_id=model.team_recipient_id,
            _agent_id=model.agent_id,
            _can_claim=model.can_claim,
            _notified_at=model.notified_at,
            _acknowledged_at=model.acknowledged_at,
            _claimed_at=model.claimed_at,
        )
