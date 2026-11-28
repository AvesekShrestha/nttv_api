import pytest

from src.domain.exceptions.invalid_notification_state import (
    InvalidNotificationStateError,
)
from src.domain.notification.notification_aggregate import (
    NotificationAggregrate,
)
from src.domain.notification.notification_channel import NotificationChannel
from src.domain.notification.notification_status import NotificationStatus


def make_notification() -> NotificationAggregrate:
    return NotificationAggregrate.create(
        id="NOT-001",
        recipient="test@example.com",
        channel=NotificationChannel.EMAIL,
        subject="Test notification",
        message="Test message",
    )


def test_new_notification_is_pending():
    notification = make_notification()

    assert notification.id == "NOT-001"
    assert notification.status == NotificationStatus.PENDING
    assert notification.attempt_count == 0
    assert notification.created_at is not None
    assert notification.sent_at is None


def test_mark_as_sending():
    notification = make_notification()

    notification.mark_as_sending()

    assert notification.status == NotificationStatus.SENDING


def test_mark_as_sent():
    notification = make_notification()
    notification.mark_as_sending()

    notification.mark_as_sent()

    assert notification.status == NotificationStatus.SENT
    assert notification.sent_at is not None


def test_mark_as_failed():
    notification = make_notification()
    notification.mark_as_sending()

    notification.mark_as_failed("SMTP unavailable")

    assert notification.status == NotificationStatus.FAILED
    assert notification.last_error == "SMTP unavailable"
    assert notification.failed_at is not None


def test_failed_notification_can_be_retried():
    notification = make_notification()
    notification.mark_as_sending()
    notification.mark_as_failed("SMTP unavailable")

    notification.mark_as_sending()

    assert notification.status == NotificationStatus.SENDING
    assert notification.last_error is None
    assert notification.failed_at is None


def test_cannot_mark_pending_as_sent():
    notification = make_notification()

    with pytest.raises(InvalidNotificationStateError):
        notification.mark_as_sent()


def test_cannot_mark_pending_as_failed():
    notification = make_notification()

    with pytest.raises(InvalidNotificationStateError):
        notification.mark_as_failed("Error")


def test_cannot_send_already_sent_notification():
    notification = make_notification()
    notification.mark_as_sending()
    notification.mark_as_sent()

    with pytest.raises(InvalidNotificationStateError):
        notification.mark_as_sending()
