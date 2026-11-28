import asyncio
import logging

from confluent_kafka import Consumer, KafkaError
from sqlalchemy.exc import SQLAlchemyError

from analytics.application.analytics_event.analytics_event_service_interface import (
    IAnalyticsEventService,
)
from analytics.application.shared.application_exception import ApplicationException
from analytics.domain.events.kafka_event import KafkaEvent
from analytics.domain.shared.domain_exception import DomainException

logger = logging.getLogger(__name__)


class EventIngestion:

    def __init__(
        self,
        analytics_event_service: IAnalyticsEventService,
    ) -> None:

        self._analytics_event_service = analytics_event_service

        self._consumer = Consumer(
            {
                "bootstrap.servers": "localhost:9092",
                "group.id": "ticket-analytics-ingestion",
                "enable.auto.commit": False,
                "enable.auto.offset.store": False,
                "auto.offset.reset": "earliest",
            }
        )

        self._running = False

    async def start(self) -> None:

        self._running = True

        self._consumer.subscribe(["ticket.events"])

        logger.info("Analytics Kafka ingestion worker started.")

        try:
            while self._running:

                message = await asyncio.to_thread(
                    self._consumer.poll,
                    1.0,
                )

                if message is None:
                    continue

                error = message.error()

                if error is not None:

                    if error.code() == KafkaError._PARTITION_EOF:
                        continue

                    raise RuntimeError(f"Kafka error: {error}")

                try:
                    print("Hello")
                    await self._process_message(message)

                    # Commit only after successful database persistence.
                    await asyncio.to_thread(
                        self._consumer.commit,
                        message=message,
                        asynchronous=False,
                    )

                except (ApplicationException, DomainException) as e:
                    logger.exception(e.message)

                except Exception:
                    logger.exception(
                        "Failed to ingest Kafka event. "
                        "Topic=%s Partition=%s Offset=%s",
                        message.topic(),
                        message.partition(),
                        message.offset(),
                    )
                    raise

        finally:
            await asyncio.to_thread(self._consumer.close)
            logger.info("Analytics Kafka ingestion worker stopped.")

    async def _process_message(self, message) -> None:

        payload = message.value()
        print(payload)

        if payload is None:
            raise ValueError("Kafka message payload is empty")

        event = KafkaEvent.model_validate_json(payload)
        print(event)

        print(f"Received event with id : {event.id} and type : {event.event_type}")
        logger.info(
            "Received event: %s | Event ID: %s",
            event.event_type,
            event.id,
        )

        await self._analytics_event_service.register_event(
            event_id=event.id,
            event_type=event.event_type,
            payload=event.model_dump(mode="json"),
        )

        print("after the register event")

        logger.info(
            "Successfully persisted event: %s | Event ID: %s",
            event.event_type,
            event.id,
        )

    def stop(self) -> None:
        self._running = False
