from abc import ABC, abstractmethod

from src.domain.outbox.entity.outbox_event import OutboxEvent


class IOutboxRepository(ABC):

    @abstractmethod
    async def add(self, event: OutboxEvent) -> None:
        pass

    @abstractmethod
    async def get_unpublished(
        self,
        limit: int = 100,
    ) -> list[OutboxEvent]:
        pass

    @abstractmethod
    async def update(self, event: OutboxEvent) -> None:
        pass
