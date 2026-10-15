from ticket.domain.assignment.assignment_status import AssignmentStatus
from ticket.domain.assignment.assignment_type import AssignmentType
from ticket.domain.assignment.assignment_aggregate import AssignmentAggregate
from ticket.domain.assignment.entity.team_recipient_entity import TeamRecipientEntity
from ticket.domain.assignment.entity.agent_recipient_entity import AgentRecipientEntity

from ticket.infrastructure.persistence.sqlalchemy.models.assignment_model import Assignment
from ticket.infrastructure.persistence.sqlalchemy.models.assignment_team_recipient_model import AssignmentTeamRecipient
from ticket.infrastructure.persistence.sqlalchemy.models.assignment_agent_recipient_model import AssignmentAgentRecipient


class AssignmentMapper:

    @staticmethod
    def to_domain(model: Assignment) -> AssignmentAggregate:

        team_recipients = [
            TeamRecipientEntity(
                _id=team.id,
                _team_id=team.team_id,
                _agents=[
                    AgentRecipientEntity(
                        _id=agent.id,
                        _agent_id=agent.agent_id,
                        _can_claim=agent.can_claim,
                        _notified_at=agent.notified_at,
                        _acknowledged_at=agent.acknowledged_at,
                        _claimed_at=agent.claimed_at,
                    )
                    for agent in team.agent_recipients
                ],
            )
            for team in model.team_recipients
        ]

        return AssignmentAggregate(
            _id=model.id,
            _ticket_id=model.ticket_id,
            _assigned_by=model.assigned_by,
            _assignment_type=AssignmentType.from_string(model.assignment_type),
            _status=AssignmentStatus.from_string(model.status),
            _primary_agent_id=model.primary_agent_id,
            _responsible_agent_id=model.responsible_agent_id,
            _team_recipients=team_recipients,
            _assigned_at=model.assigned_at,
            _acknowledgment_deadline_at=model.acknowledgment_deadline_at,
            _resolution_deadline_at=model.resolution_deadline_at,
            _acknowledgment_sla_breached_at=(
                model.acknowledgment_sla_breached_at
            ),
            _resolution_sla_breached_at=model.resolution_sla_breached_at,
            _started_at=model.started_at,
            _acknowledged_at=model.acknowledged_at,
            _completed_at=model.completed_at,
            _created_at=model.created_at,
            _updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(
        aggregate: AssignmentAggregate,
    ) -> Assignment:

        model = Assignment(
            id=aggregate.id,
            ticket_id=aggregate.ticket_id,
            assigned_by=aggregate.assigned_by,
            assignment_type=aggregate.assignment_type.value,
            status=aggregate.status.value,
            primary_agent_id=aggregate.primary_agent_id,
            responsible_agent_id=aggregate.responsible_agent_id,
            assigned_at=aggregate.assigned_at,
            acknowledgment_deadline_at=(
                aggregate.acknowledgment_deadline_at
            ),
            resolution_deadline_at=aggregate.resolution_deadline_at,
            acknowledgment_sla_breached_at=(
                aggregate.acknowledgment_sla_breached_at
            ),
            resolution_sla_breached_at=aggregate.resolution_sla_breached_at,
            started_at=aggregate.started_at,
            acknowledged_at=aggregate._acknowledged_at,
            completed_at=aggregate.completed_at,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

        model.team_recipients = [
            AssignmentTeamRecipient(
                id=team.id,
                team_id=team.team_id,
                agent_recipients=[
                    AssignmentAgentRecipient(
                        id=agent.id,
                        agent_id=agent.agent_id,
                        can_claim=agent.can_claim,
                        notified_at=agent.notified_at,
                        acknowledged_at=agent.acknowledged_at,
                        claimed_at=agent.claimed_at,
                    )
                    for agent in team.agents
                ],
            )
            for team in aggregate.team_recipients
        ]

        return model
