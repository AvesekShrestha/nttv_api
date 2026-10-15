from abc import ABC, abstractmethod

from ticket.application.events.kafka_event import KafkaEvent


class IProducer(ABC):
    @abstractmethod
    async def produce(self, event : KafkaEvent) -> None : pass
