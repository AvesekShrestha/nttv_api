from uuid import UUID

import pytest

from src.domain.notification.notification_aggregate import NotificationAggregrate


class FakeNotificationRepository:
    def __init__(self):
        self.notifications: list[NotificationAggregrate] = []

    async def save(self, notification: NotificationAggregrate) -> NotificationAggregrate:
        self.notifications.append(notification)
        return notification

    async def get_by_id(self, notification_id: UUID) -> NotificationAggregrate | None:
        return next(
            (n for n in self.notifications if n.id == notification_id),
            None,
        )


@pytest.fixture
def repository() -> FakeNotificationRepository:
    return FakeNotificationRepository()


@pytest.fixture
def anyio_backend():
    return "asyncio"
