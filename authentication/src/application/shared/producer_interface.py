from abc import ABC, abstractmethod

from application.events.kafka_event import KafkaEvent


class IProducer(ABC):
    @abstractmethod
    async def produce(self, event : KafkaEvent) -> None : pass

