from dataclasses import dataclass, field
from datetime import datetime, timezone

from ticket.domain.shared.aggregate import AggregrateRoot
from ticket.domain.ticket.entity.ticket_activity_entity import TicketActivityEntity
from ticket.domain.ticket.ticket_priority import TicketPriority
from ticket.domain.ticket.ticket_status import TicketStatus


@dataclass
class TicketAggregrate(AggregrateRoot[str]):
    _title: str
    _description: str
    _category_id: str
    _created_by: str

    _priority: TicketPriority = TicketPriority.MEDIUM
    _status: TicketStatus = TicketStatus.NEW
    _current_assignment_id: str | None = None
    _activities: list[TicketActivityEntity] = field(default_factory=list)
    _created_at: datetime | None = None
    _updated_at: datetime | None = None
    _resolved_at: datetime | None = None

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def category_id(self) -> str:
        return self._category_id

    @property
    def created_by(self) -> str:
        return self._created_by

    @property
    def priority(self) -> TicketPriority:
        return self._priority

    @property
    def status(self) -> TicketStatus:
        return self._status

    @property
    def current_assignment_id(self) -> str | None:
        return self._current_assignment_id

    @property
    def activities(self) -> list[TicketActivityEntity]:
        return self._activities.copy()

    @property
    def created_at(self) -> datetime | None:
        return self._created_at

    @property
    def updated_at(self) -> datetime | None:
        return self._updated_at

    @property
    def resolved_at(self) -> datetime | None:
        return self._resolved_at

    @staticmethod
    def create(
        id: str,
        title: str,
        description: str,
        category_id: str,
        created_by: str,
        priority: TicketPriority = TicketPriority.MEDIUM,
    ) -> "TicketAggregrate":
        return TicketAggregrate(
            _id=id,
            _title=title,
            _description=description,
            _category_id=category_id,
            _created_by=created_by,
            _priority=priority,
            _status=TicketStatus.NEW,
        )

    def add_activity(self, activity: TicketActivityEntity) -> None:
        self._activities.append(activity)

    def change_title(self, title: str) -> None:
        self._title = title

    def change_description(self, description: str) -> None:
        self._description = description

    def change_priority(self, priority: TicketPriority) -> None:
        self._priority = priority

    def change_status(self, status: TicketStatus) -> None:
        self._status = status

    def change_category(self, category_id: str) -> None:
        self._category_id = category_id

    def change_assignment(self, assignment_id: str | None) -> None:
        self._current_assignment_id = assignment_id

    def mark_resolved(self, resolved_at: datetime) -> None:
        self._status = TicketStatus.RESOLVED
        self._resolved_at = resolved_at
