from abc import ABC, abstractmethod

from analytics.domain.events.kafka_event import KafkaEvent


class IEventHandler(ABC):

    @property
    @abstractmethod
    def event_type(self) -> str:
        pass

    @abstractmethod
    async def handle(self, event: KafkaEvent) -> None:
        pass
