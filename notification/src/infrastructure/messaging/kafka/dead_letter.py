import asyncio
import base64
import json
from datetime import datetime, timezone

from confluent_kafka import KafkaError, Message, Producer

from src.config.settings import settings


def create_dead_letter_producer() -> Producer:
    return Producer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "acks": "all",
            "enable.idempotence": True,
        }
    )


def _publish_dead_letter(
    producer: Producer,
    message: Message,
    error: Exception,
    attempts: int,
) -> None:
    topic = message.topic()
    partition = message.partition()
    offset = message.offset()

    if topic is None or partition is None or offset is None:
        raise RuntimeError("Missing Kafka message metadata")

    raw_value = message.value()

    record = {
        "source_topic": topic,
        "source_partition": partition,
        "source_offset": offset,
        "failed_at": datetime.now(timezone.utc).isoformat(),
        "error_type": type(error).__name__,
        "error_message": str(error),
        "attempts": attempts,
        "raw_value_base64": base64.b64encode(
            raw_value if raw_value is not None else b""
        ).decode("ascii"),
    }

    delivery_error: KafkaError | None = None
    delivered = False

    def on_delivery(err: KafkaError | None, msg: Message) -> None:
        nonlocal delivered, delivery_error
        delivery_error = err
        delivered = err is None

    producer.produce(
        topic=settings.kafka_ticket_dlq_topic,
        key=f"{topic}:{partition}:{offset}".encode("utf-8"),
        value=json.dumps(record).encode("utf-8"),
        on_delivery=on_delivery,
    )

    remaining = producer.flush(10)

    if remaining != 0 or not delivered:
        raise RuntimeError(
            f"Dead-letter delivery failed: {delivery_error}"
        )


async def publish_dead_letter(
    producer: Producer,
    message: Message,
    error: Exception,
    attempts: int,
) -> None:
    await asyncio.to_thread(
        _publish_dead_letter,
        producer,
        message,
        error,
        attempts,
    )
