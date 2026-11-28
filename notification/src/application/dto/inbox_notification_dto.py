from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class InboxRecipient:
    user_id: str
    title: str
    message: str
    requires_action: bool = False
    send_email: bool = False


@dataclass(frozen=True)
class RecordTicketEventRequest:
    source_topic: str
    event_id: str
    event_type: str
    occurred_at: datetime
    ticket_id: str
    recipients: tuple[InboxRecipient, ...]
    assignment_id: str | None = None
