from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class InboxItem:
    id: str
    recipient_user_id: str
    event_type: str
    ticket_id: str
    assignment_id: str | None
    title: str
    message: str
    requires_action: bool
    created_at: datetime
    read_at: datetime | None

    @property
    def is_read(self) -> bool:
        return self.read_at is not None


@dataclass(frozen=True)
class InboxPage:
    items: list[InboxItem]
    total: int
    page: int
    limit: int
