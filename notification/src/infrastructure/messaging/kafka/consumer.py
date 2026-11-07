import asyncio
import json
import logging

from confluent_kafka import Consumer, KafkaError

from src.config.settings import settings
from src.infrastructure.messaging.kafka.event_router import (
    EventRouter,
    create_event_router,
)

logger = logging.getLogger(__name__)


def create_consumer() -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "group.id": settings.kafka_group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )


async def consume_events(
    consumer: Consumer,
    router: EventRouter,
    topic: str,
) -> None:
    consumer.subscribe([topic])
    logger.info("Subscribed to Kafka topic: %s", topic)

    while True:
        # Poll and commit on the same thread; Consumer is not thread-safe.
        message = consumer.poll(1.0)

        if message is None:
            continue

        error = message.error()

        if error is not None:
            if error.code() == KafkaError._PARTITION_EOF:
                continue

            logger.error("Kafka consumer error: %s", error)
            continue

        value = message.value()

        if value is None:
            raise ValueError(
                f"Empty Kafka message at {topic}:"
                f"{message.partition()}:{message.offset()}"
            )

        try:
            payload = json.loads(value)

            if not isinstance(payload, dict):
                raise ValueError("Event payload must be a JSON object")

            await router.dispatch(topic, payload)

        except Exception:
            logger.exception(
                "Event processing failed; message not committed. "
                "topic=%s partition=%s offset=%s",
                message.topic(),
                message.partition(),
                message.offset(),
            )
            raise

        consumer.commit(message=message, asynchronous=False)

        logger.info(
            "Committed topic=%s partition=%s offset=%s",
            message.topic(),
            message.partition(),
            message.offset(),
        )


async def consume_ticket_events() -> None:
    topic = settings.kafka_ticket_topic
    consumer = create_consumer()
    router = create_event_router(topic)

    try:
        await consume_events(consumer, router, topic)
    finally:
        consumer.close()
        logger.info("Kafka consumer closed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(consume_ticket_events())
