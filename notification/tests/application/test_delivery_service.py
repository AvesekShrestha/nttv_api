import pytest

from unittest.mock import AsyncMock, MagicMock

from src.application.delivery.delivery_service import DeliveryService
from src.application.exceptions.delivery_exception import DeliveryError
from src.domain.notification.notification_aggregate import (
    NotificationAggregrate,
)
from src.domain.notification.notification_channel import NotificationChannel
from src.domain.notification.notification_status import NotificationStatus


def make_notification() -> NotificationAggregrate:
    notification = NotificationAggregrate.create(
        id="NOT-001",
        recipient="test@example.com",
        channel=NotificationChannel.EMAIL,
        subject="Test subject",
        message="Test message",
    )

    notification.mark_as_sending()
    return notification


@pytest.fixture
def repository():
    repo = MagicMock()
    repo.claim_for_delivery = AsyncMock(return_value=True)
    repo.get_by_id = AsyncMock()
    repo.save = AsyncMock(return_value=True)
    return repo


@pytest.fixture
def email_sender():
    sender = MagicMock()
    sender.send = AsyncMock()
    return sender


@pytest.mark.asyncio
async def test_successful_email_delivery(repository, email_sender):
    notification = make_notification()
    repository.get_by_id.return_value = notification

    service = DeliveryService(repository, email_sender)

    await service.deliver(notification.id)

    repository.claim_for_delivery.assert_awaited_once_with(
        notification.id
    )

    email_sender.send.assert_awaited_once_with(
        "test@example.com",
        "Test subject",
        "Test message",
    )

    assert notification.status == NotificationStatus.SENT
    repository.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_email_delivery_failure(repository, email_sender):
    notification = make_notification()
    repository.get_by_id.return_value = notification

    email_sender.send.side_effect = DeliveryError(
        "SMTP unavailable"
    )

    service = DeliveryService(repository, email_sender)

    await service.deliver(notification.id)

    assert notification.status == NotificationStatus.FAILED
    assert notification.last_error == "SMTP unavailable"
    repository.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_duplicate_claim_is_skipped(repository, email_sender):
    repository.claim_for_delivery.return_value = False

    service = DeliveryService(repository, email_sender)

    await service.deliver("NOT-001")

    email_sender.send.assert_not_awaited()
    repository.get_by_id.assert_not_awaited()
    repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_claimed_notification_not_found(repository, email_sender):
    repository.get_by_id.return_value = None

    service = DeliveryService(repository, email_sender)

    with pytest.raises(RuntimeError, match="not found"):
        await service.deliver("NOT-001")

    email_sender.send.assert_not_awaited()


@pytest.mark.asyncio
async def test_unexpected_notification_status(repository, email_sender):
    notification = make_notification()
    notification.mark_as_sent()

    repository.get_by_id.return_value = notification

    service = DeliveryService(repository, email_sender)

    with pytest.raises(RuntimeError, match="Unexpected notification status"):
        await service.deliver(notification.id)

    email_sender.send.assert_not_awaited()


@pytest.mark.asyncio
async def test_unexpected_email_error_propagates(repository, email_sender):
    notification = make_notification()
    repository.get_by_id.return_value = notification

    email_sender.send.side_effect = RuntimeError(
        "Unexpected email sender failure"
    )

    service = DeliveryService(repository, email_sender)

    with pytest.raises(RuntimeError, match="Unexpected email sender"):
        await service.deliver(notification.id)

    assert notification.status == NotificationStatus.SENDING
