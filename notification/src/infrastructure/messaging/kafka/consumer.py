import asyncio
import logging

from confluent_kafka import Consumer, KafkaError, KafkaException, Producer

from src.config.settings import settings
from src.infrastructure.messaging.kafka.consumer_factory import (
    create_consumer,
)
from src.infrastructure.messaging.kafka.dead_letter import (
    create_dead_letter_producer,
)
from src.infrastructure.messaging.kafka.event_router import (
    EventRouter,
    create_event_router,
)
from src.infrastructure.messaging.kafka.message_processor import (
    process_message,
)
from src.infrastructure.messaging.kafka.retry_policy import RetryPolicy

logger = logging.getLogger(__name__)


async def consume_events(
    consumer: Consumer,
    producer: Producer,
    router: EventRouter,
    topics: list[str],
    retry_policy: RetryPolicy,
) -> None:
    consumer.subscribe(topics)

    logger.info(
        "Subscribed to Kafka topics: %s",
        ", ".join(topics),
    )

    while True:
        message = await asyncio.to_thread(consumer.poll, 1.0)

        if message is None:
            continue

        error = message.error()

        if error is not None:
            if error.code() == KafkaError._PARTITION_EOF:
                continue

            if error.fatal():
                logger.error(
                    "Fatal Kafka consumer error: %s",
                    error,
                )
                raise KafkaException(error)

            logger.error("Kafka consumer error: %s", error)
            await asyncio.sleep(retry_policy.delay_seconds)
            continue

        await process_message(
            consumer=consumer,
            producer=producer,
            router=router,
            message=message,
            retry_policy=retry_policy,
        )


async def consume_notification_events() -> None:
    topics = [
        settings.kafka_ticket_topic,
        settings.kafka_auth_topic,
    ]

    retry_policy = RetryPolicy(
        max_attempts=settings.kafka_max_retries,
        delay_seconds=settings.kafka_retry_delay_seconds,
    )

    consumer = create_consumer()

    try:
        producer = create_dead_letter_producer()

        try:
            router = create_event_router(
                ticket_topic=settings.kafka_ticket_topic,
                auth_topic=settings.kafka_auth_topic,
            )

            await consume_events(
                consumer=consumer,
                producer=producer,
                router=router,
                topics=topics,
                retry_policy=retry_policy,
            )

        finally:
            remaining = await asyncio.to_thread(
                producer.flush,
                10,
            )

            if remaining:
                logger.error(
                    "%s DLT producer message(s) remain undelivered",
                    remaining,
                )

    finally:
        await asyncio.to_thread(consumer.close)
        logger.info("Kafka consumer closed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    try:
        asyncio.run(consume_notification_events())

    except KeyboardInterrupt:
        logger.info("Kafka consumer stopped by user")

    except Exception:
        logger.exception(
            "Kafka consumer stopped due to a fatal error"
        )
        raise
