from ticket.domain.ticket.ticket_aggregate import TicketAggregrate
from ticket.domain.ticket.entity.ticket_activity_entity import TicketActivityEntity
from ticket.domain.ticket.ticket_priority import TicketPriority
from ticket.domain.ticket.ticket_status import TicketStatus
from ticket.infrastructure.persistence.sqlalchemy.models.ticket_model import Ticket
from ticket.infrastructure.persistence.sqlalchemy.mappers.activity_mapper import TicketActivityMapper



class TicketMapper:

    @staticmethod
    def to_model(aggregate: TicketAggregrate) -> Ticket:
        return Ticket(
            id=aggregate.id,
            title=aggregate.title,
            description=aggregate.description,
            priority=aggregate.priority.value,
            status=aggregate.status.value,
            current_assignment_id=aggregate.current_assignment_id,
            category_id=aggregate.category_id,
            created_by=aggregate.created_by,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
            resolved_at=aggregate.resolved_at,
        )

    @staticmethod
    def to_domain(model: Ticket) -> TicketAggregrate:
        return TicketAggregrate(
            _id=model.id,
            _title=model.title,
            _description=model.description,
            _category_id=model.category_id,
            _created_by=model.created_by,
            _priority=TicketPriority.from_string(model.priority),
            _status=TicketStatus.from_string(model.status),
            _current_assignment_id=model.current_assignment_id,
            _created_at=model.created_at,
            _updated_at=model.updated_at,
            _resolved_at=model.resolved_at,
        )
