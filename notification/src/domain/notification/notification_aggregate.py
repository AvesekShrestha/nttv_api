from dataclasses import dataclass
from datetime import datetime, timezone

from src.domain.notification.notification_channel import NotificationChannel
from src.domain.notification.notification_status import NotificationStatus
from src.domain.shared.aggregate import AggregrateRoot


@dataclass
class NotificationAggregrate(AggregrateRoot[str]):
    _recipient: str
    _channel: NotificationChannel
    _subject: str
    _message: str
    _status: NotificationStatus = NotificationStatus.PENDING
    _created_at: datetime | None = None
    _sent_at: datetime | None = None
    _failed_at: datetime | None = None

    @property
    def recipient(self) -> str:
        return self._recipient

    @property
    def channel(self) -> NotificationChannel:
        return self._channel

    @property
    def subject(self) -> str:
        return self._subject

    @property
    def message(self) -> str:
        return self._message

    @property
    def status(self) -> NotificationStatus:
        return self._status

    @property
    def created_at(self) -> datetime | None:
        return self._created_at

    @property
    def sent_at(self) -> datetime | None:
        return self._sent_at

    @property
    def failed_at(self) -> datetime | None:
        return self._failed_at

    @staticmethod
    def create(
        id: str,
        recipient: str,
        channel: NotificationChannel,
        subject: str,
        message: str,
    ) -> "NotificationAggregrate":
        return NotificationAggregrate(
            _id=id,
            _recipient=recipient,
            _channel=channel,
            _subject=subject,
            _message=message,
            _status=NotificationStatus.PENDING,
            _created_at=datetime.now(timezone.utc),
        )

    def mark_as_sending(self) -> None:
        if self._status != NotificationStatus.PENDING:
            raise ValueError("Notification must be pending before sending")

        self._status = NotificationStatus.SENDING

    def mark_as_sent(self) -> None:
        if self._status != NotificationStatus.SENDING:
            raise ValueError("Notification must be sending before marking as sent")

        self._status = NotificationStatus.SENT
        self._sent_at = datetime.now(timezone.utc)

    def mark_as_failed(self, error: str) -> None:
        if self._status != NotificationStatus.SENDING:
            raise ValueError("Notification must be sending before marking as failed")

        self._status = NotificationStatus.FAILED
        self._last_error = error
        self._failed_at = datetime.now(timezone.utc)
