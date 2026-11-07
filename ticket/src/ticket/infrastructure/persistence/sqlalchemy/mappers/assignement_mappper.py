from ticket.domain.assignment.assignment_aggregate import AssignmentAggregate
from ticket.domain.assignment.assignment_status import AssignmentStatus
from ticket.domain.assignment.assignment_type import AssignmentType

from ticket.infrastructure.persistence.sqlalchemy.models.assignment_model import (
    Assignment,
)

from ticket.infrastructure.persistence.sqlalchemy.mappers.team_recipient_mapper import (
    TeamRecipientMapper,
)


class AssignmentMapper:

    @staticmethod
    def to_model(aggregate: AssignmentAggregate) -> Assignment:

        return Assignment(
            id=aggregate.id,
            ticket_id=aggregate.ticket_id,
            assignment_type=aggregate.assignment_type.value,
            status=aggregate.status.value,
            primary_agent_id=aggregate.primary_agent_id,
            responsible_agent_id=aggregate.responsible_agent_id,
            assigned_by=aggregate.assigned_by,
            assigned_at=aggregate.assigned_at,
            acknowledgment_deadline_at=aggregate.acknowledgment_deadline_at,
            resolution_deadline_at=aggregate.resolution_deadline_at,
            acknowledgment_sla_breached_at=aggregate.acknowledgment_sla_breached_at,
            resolution_sla_breached_at=aggregate.resolution_sla_breached_at,
            acknowledged_at=aggregate.acknowledged_at,
            completed_at=aggregate.completed_at,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,

            team_recipients=[
                TeamRecipientMapper.to_model(recipient)
                for recipient in aggregate.team_recipients
            ],
        )

    @staticmethod
    def to_domain(model: Assignment) -> AssignmentAggregate:

        return AssignmentAggregate(
            _id=model.id,
            _ticket_id=model.ticket_id,
            _assignment_type=AssignmentType.from_string(
                model.assignment_type
            ),
            _status=AssignmentStatus.from_string(model.status),
            _primary_agent_id=model.primary_agent_id,
            _responsible_agent_id=model.responsible_agent_id,
            _assigned_by=model.assigned_by,

            _team_recipients=[
                TeamRecipientMapper.to_domain(recipient)
                for recipient in model.team_recipients
            ],

            _assigned_at=model.assigned_at,
            _acknowledgment_deadline_at=model.acknowledgment_deadline_at,
            _resolution_deadline_at=model.resolution_deadline_at,
            _acknowledgment_sla_breached_at=model.acknowledgment_sla_breached_at,
            _resolution_sla_breached_at=model.resolution_sla_breached_at,
            _acknowledged_at=model.acknowledged_at,
            _completed_at=model.completed_at,
            _created_at=model.created_at,
            _updated_at=model.updated_at,
        )

