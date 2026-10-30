from ticket.domain.ticket.entity.ticket_activity_entity import TicketActivityEntity

from ticket.infrastructure.persistence.sqlalchemy.models.activities_model import TicketActivity

class TicketActivityMapper:
    @staticmethod
    def to_entity(model: TicketActivity) -> TicketActivityEntity:
        return TicketActivityEntity(
            _id=model.id,
            _ticket_id=model.ticket_id,
            _activity_type=model.activity_type,
            _actor_id=model.actor_id,
            _created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: TicketActivityEntity) -> TicketActivity:
        return TicketActivity(
            id=entity.id,
            ticket_id=entity.ticket_id,
            activity_type=entity.activity_type,
            actor_id=entity.actor_id,
            created_at=entity.created_at,
        )
