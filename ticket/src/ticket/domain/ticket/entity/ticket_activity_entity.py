from dataclasses import dataclass
from datetime import datetime

from ticket.domain.shared.entity import Entity


@dataclass
class TicketActivityEntity(Entity[str]):
    _ticket_id: str
    _activity_type: str
    _actor_id: str
    _created_at: datetime | None = None

    @property
    def ticket_id(self) -> str:
        return self._ticket_id

    @property
    def activity_type(self) -> str:
        return self._activity_type

    @property
    def actor_id(self) -> str:
        return self._actor_id

    @property
    def created_at(self) -> datetime | None:
        return self._created_at

    @staticmethod
    def create(
        id: str,
        ticket_id: str,
        activity_type: str,
        actor_id: str,
    ) -> TicketActivityEntity:
        return TicketActivityEntity(
            _id=id,
            _ticket_id=ticket_id,
            _activity_type=activity_type,
            _actor_id=actor_id,
        )
