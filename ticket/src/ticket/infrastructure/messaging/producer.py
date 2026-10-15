import socket

from confluent_kafka.aio import AIOProducer

from ticket.application.events.kafka_event import KafkaEvent
from ticket.application.shared.producer_interface import IProducer


class KafkaProducer(IProducer):
    def __init__(self) -> None:
        config = {
            "bootstrap.servers": "localhost:9092",
            "client.id": socket.gethostname(),
            "acks": "all",
        }

        self.producer = AIOProducer(config)

    async def produce(self, event: KafkaEvent) -> None:
        delivery_future = await self.producer.produce(
            topic="auth.events",
            key=event.key,
            value=event.model_dump_json(),
        )

        # Wait for Kafka to confirm delivery.
        # Raises an exception if delivery fails.
        message = await delivery_future

        print(
            f"Event published successfully: "
            f"{message.topic()} [{message.partition()}] "
            f"offset={message.offset()}"
        )

    async def close(self) -> None:
        await self.producer.close()
