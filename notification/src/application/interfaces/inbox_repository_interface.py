from abc import ABC, abstractmethod

from src.application.dto.inbox_notification_dto import (
    RecordTicketEventRequest,
)


class InboxRepositoryInterface(ABC):
    @abstractmethod
    async def record_event(
        self,
        request: RecordTicketEventRequest,
    ) -> bool:
        """
        Atomically save the event's notification work.

        Return True when saved.
        Return False when the event was already processed.
        """
        raise NotImplementedError
