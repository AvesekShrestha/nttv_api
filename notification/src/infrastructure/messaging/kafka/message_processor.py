import asyncio
import logging

from confluent_kafka import Consumer, Message, Producer
from pydantic import ValidationError

from src.infrastructure.messaging.kafka.dead_letter import (
    publish_dead_letter,
)
from src.infrastructure.messaging.kafka.event_router import (
    EventRouter,
    UnknownEventHandlerError,
)
from src.infrastructure.messaging.kafka.message_parser import (
    InvalidMessageError,
    parse_message,
)
from src.infrastructure.messaging.kafka.retry_policy import RetryPolicy
from src.application.exceptions.delivery_exception import (
    PermanentDeliveryError,
)

logger = logging.getLogger(__name__)


def commit_message(
    consumer: Consumer,
    message: Message,
) -> None:
    partitions = consumer.commit(
        message=message,
        asynchronous=False,
    )

    if not partitions:
        raise RuntimeError("Kafka commit returned no results")

    for partition in partitions:
        if partition.error is not None:
            raise RuntimeError(
                f"Kafka commit failed: {partition.error}"
            )

    logger.info(
        "Committed topic=%s partition=%s offset=%s",
        message.topic(),
        message.partition(),
        message.offset(),
    )


async def reject_message(
    consumer: Consumer,
    producer: Producer,
    message: Message,
    error: Exception,
    attempts: int,
) -> None:
    try:
        await publish_dead_letter(
            producer=producer,
            message=message,
            error=error,
            attempts=attempts,
        )

    except Exception:
        logger.exception(
            "DLT publication failed; source offset not committed. "
            "topic=%s partition=%s offset=%s",
            message.topic(),
            message.partition(),
            message.offset(),
        )
        raise

    logger.warning(
        "Event sent to DLT. topic=%s partition=%s offset=%s "
        "error_type=%s attempts=%s",
        message.topic(),
        message.partition(),
        message.offset(),
        type(error).__name__,
        attempts,
    )

    commit_message(consumer, message)


async def process_message(
    consumer: Consumer,
    producer: Producer,
    router: EventRouter,
    message: Message,
    retry_policy: RetryPolicy,
) -> None:
    topic = message.topic()
    partition = message.partition()
    offset = message.offset()

    if topic is None or partition is None or offset is None:
        raise RuntimeError(
            "Kafka message missing topic, partition, or offset"
        )

    try:
        payload = parse_message(message)

    except InvalidMessageError as exc:
        logger.warning(
            "Invalid Kafka payload. "
            "topic=%s partition=%s offset=%s error_type=%s",
            topic,
            partition,
            offset,
            type(exc).__name__,
        )

        await reject_message(
            consumer,
            producer,
            message,
            exc,
            attempts=1,
        )
        return

    for attempt in range(1, retry_policy.max_attempts + 1):
        try:
            await router.dispatch(topic, payload)

        except (
            ValidationError,
            UnknownEventHandlerError,
            PermanentDeliveryError,
        ) as exc:
            logger.warning(
                "Kafka event rejected. "
                "topic=%s partition=%s offset=%s error_type=%s",
                topic,
                partition,
                offset,
                type(exc).__name__,
            )

            await reject_message(
                consumer,
                producer,
                message,
                exc,
                attempts=attempt,
            )
            return

        except Exception as exc:
            # Log metadata only. Exception text and tracebacks can
            # contain validation input or SMTP recipient details.
            logger.warning(
                "Event processing failed. attempt=%s/%s "
                "topic=%s partition=%s offset=%s error_type=%s",
                attempt,
                retry_policy.max_attempts,
                topic,
                partition,
                offset,
                type(exc).__name__,
            )

            if not retry_policy.should_retry(attempt):
                await reject_message(
                    consumer,
                    producer,
                    message,
                    exc,
                    attempts=attempt,
                )
                return

            await asyncio.sleep(retry_policy.delay_seconds)

        else:
            commit_message(consumer, message)
            return
