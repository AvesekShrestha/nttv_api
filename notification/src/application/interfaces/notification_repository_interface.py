from abc import ABC, abstractmethod

from src.domain.notification.notification_aggregate import NotificationAggregrate


class NotificationRepositoryInterface(ABC):
    @abstractmethod
    async def save(
        self,
        notification: NotificationAggregrate,
        *,
        source_event_id: str | None = None,
    ) -> bool:
        pass

    @abstractmethod
    async def get_by_id(
        self,
        notification_id: str,
    ) -> NotificationAggregrate | None:
        pass

    @abstractmethod
    async def exists_by_source_event(
        self,
        source_event_id: str,
        recipient: str,
    ) -> bool:
        pass
