import asyncio
import logging
import os

from confluent_kafka import Consumer, KafkaError
from dotenv import load_dotenv
from pydantic import ValidationError

from src.application.dto.create_notification_dto import CreateNotificationRequest
from src.application.notification.create_notification import CreateNotification
from src.domain.notification.notification_channel import NotificationChannel
from src.infrastructure.identity.id_generator import IdGenerator
from src.infrastructure.messaging.kafka.ticket_event import TicketEvent
from src.infrastructure.persistence.sqlalchemy.database import SessionLocal
from src.infrastructure.persistence.sqlalchemy.repositories.notification_repository import (
    SQLAlchemyNotificationRepository,
)

load_dotenv()
logger = logging.getLogger(__name__)


def create_consumer() -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": os.environ["KAFKA_BOOTSTRAP_SERVERS"],
            "group.id": os.environ["KAFKA_GROUP_ID"],
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )

async def process_ticket_event(event: TicketEvent) -> None:
    async with SessionLocal() as session:
        try:
            repository = SQLAlchemyNotificationRepository(session)
            id_generator = IdGenerator()
            use_case = CreateNotification(repository, id_generator)

            for recipient in event.recipients:
                dto = CreateNotificationRequest(
                    recipient=str(recipient.email),
                    channel=NotificationChannel.EMAIL,
                    subject=f"[{event.subject.priority}] {event.subject.title}",
                    message=(
                        f"Ticket event: {event.event_type}\n"
                        f"Category: {event.subject.category_id}\n"
                        f"Priority: {event.subject.priority}\n"
                        f"Level: {event.subject.level}\n"
                        f"Occurred at: {event.occurred_at.isoformat()}"
                    ),
                )

                notification = await use_case.execute(
                    dto,
                    source_event_id=event.event_id,
                )

                if notification is None:
                    logger.info(
                        "Skipping duplicate notification event_id=%s recipient=%s",
                        event.event_id,
                        recipient.email,
                    )
                else:
                    logger.info(
                        "Created notification id=%s event_id=%s recipient=%s",
                        notification.id,
                        event.event_id,
                        recipient.email,
                    )

        except Exception:
            logger.exception(
                "Database/session failure for event_id=%s",
                event.event_id,
            )
            raise
        finally:
            if session.in_transaction():
                await session.rollback()


async def consume_ticket_events() -> None:
    consumer = create_consumer()
    topic = os.environ["KAFKA_TICKET_TOPIC"]

    try:
        consumer.subscribe([topic])
        logger.info("Subscribed to Kafka topic: %s", topic)

        while True:
            message = await asyncio.to_thread(consumer.poll, 1.0)

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
                logger.error("Received Kafka message with no value")
                continue

            try:
                event = TicketEvent.model_validate_json(value)
            except (ValidationError, ValueError):
                logger.exception("Invalid ticket event; offset not committed")
                continue

            try:
                await process_ticket_event(event)
            except Exception:
                logger.exception(
                    "Failed to process event_id=%s; offset not committed",
                    event.event_id,
                )
                continue

            await asyncio.to_thread(
                consumer.commit,
                message=message,
                asynchronous=False,
            )
            logger.info(
                "Committed event_id=%s topic=%s partition=%s offset=%s",
                event.event_id,
                message.topic(),
                message.partition(),
                message.offset(),
            )

    finally:
        await asyncio.to_thread(consumer.close)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(consume_ticket_events())
