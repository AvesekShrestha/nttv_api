from uuid import UUID

import pytest

from src.application.dto.create_notification import CreateNotificationRequest
from src.application.use_cases.create_notification import CreateNotification
from src.domain.notification.notification import Notification
from src.domain.notification.notification_channel import NotificationChannel
from src.domain.notification.notification_status import NotificationStatus



@pytest.mark.anyio
async def test_create_notification(repository):
    use_case = CreateNotification(repository)

    request = CreateNotificationRequest(
        recipient="user@example.com",
        channel=NotificationChannel.EMAIL,
        subject="Test notification",
        message="Hello from NTC",
    )

    result = await use_case.execute(request)

    assert result.status == NotificationStatus.PENDING
    assert result.recipient == "user@example.com"
    assert repository.notifications == [result]
