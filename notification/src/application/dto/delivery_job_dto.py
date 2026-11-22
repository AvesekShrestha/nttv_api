from dataclasses import dataclass


@dataclass(frozen=True)
class ClaimedDelivery:
    id: str
    notification_id: str
    recipient_user_id: str
    subject: str
    message: str
    destination: str | None
    attempt_count: int
