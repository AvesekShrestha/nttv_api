from abc import ABC, abstractmethod

from src.application.dto.inbox_query_dto import InboxItem, InboxPage


class InboxAccessRepositoryInterface(ABC):
    @abstractmethod
    async def list_for_user(
        self,
        user_id: str,
        *,
        page: int = 1,
        limit: int = 20,
        unread_only: bool = False,
    ) -> InboxPage:
        raise NotImplementedError

    @abstractmethod
    async def get_for_user(
        self,
        user_id: str,
        notification_id: str,
    ) -> InboxItem | None:
        raise NotImplementedError

    @abstractmethod
    async def count_unread(self, user_id: str) -> int:
        raise NotImplementedError

    @abstractmethod
    async def mark_read(
        self,
        user_id: str,
        notification_id: str,
    ) -> InboxItem | None:
        raise NotImplementedError

    @abstractmethod
    async def mark_all_read(self, user_id: str) -> int:
        raise NotImplementedError
