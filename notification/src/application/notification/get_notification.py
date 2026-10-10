from src.application.interfaces.notification_repository_interface import (
    NotificationRepositoryInterface,
)
from src.domain.exceptions.notification_exception import NotificationNotFoundError
from src.domain.notification.notification_aggregate import NotificationAggregrate


class GetNotification:
    def __init__(self, repository: NotificationRepositoryInterface):
        self.repository = repository

    async def execute(self, notification_id: str) -> NotificationAggregrate:
        notification = await self.repository.get_by_id(notification_id)

        if notification is None:
            raise NotificationNotFoundError(notification_id)

        return notification
