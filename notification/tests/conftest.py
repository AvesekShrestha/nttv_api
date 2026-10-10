from uuid import UUID

import pytest

from src.domain.notification.notification import Notification


class FakeNotificationRepository:
    def __init__(self):
        self.notifications: list[Notification] = []

    async def save(self, notification: Notification) -> Notification:
        self.notifications.append(notification)
        return notification

    async def get_by_id(self, notification_id: UUID) -> Notification | None:
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
