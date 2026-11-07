from abc import ABC, abstractmethod

from ticket.domain.event.entity.processed_event_entity import ProcessedEventEntity

class IProcessedEventRepository(ABC):

    @abstractmethod
    async def exists(
        self,
        event_id: str,
    ) -> bool:
        pass

    @abstractmethod
    async def add(
        self,
        event: ProcessedEventEntity
    ) -> None:
        pass
