from uuid import uuid4

import pytest

from src.application.dto.create_notification import CreateNotificationRequest
from src.application.use_cases.create_notification import CreateNotification
from src.application.use_cases.get_notification import GetNotification
from src.domain.notification.notification_channel import NotificationChannel
from src.domain.exceptions.notification_exception import NotificationNotFoundError


@pytest.mark.anyio
async def test_get_notification_returns_existing(repository):
    created = await CreateNotification(repository).execute(
        CreateNotificationRequest(
            recipient="user@example.com",
            channel=NotificationChannel.EMAIL,
            subject="Hello",
            message="Test",
        )
    )

    result = await GetNotification(repository).execute(created.id)

    assert result == created


@pytest.mark.anyio
async def test_get_notification_raises_when_missing(repository):
    with pytest.raises(NotificationNotFoundError):
        await GetNotification(repository).execute(uuid4())
