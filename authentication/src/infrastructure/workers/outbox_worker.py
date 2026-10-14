import asyncio
import logging

from application.auth.auth_service import IDateTimeProvider, IUnitOfWork
from application.events.kafka_event import KafkaEvent
from application.interfaces.outbox_repository_interface import IOutboxRepository
from application.shared.application_exception import ApplicationException
from application.shared.producer_interface import IProducer

from domain.outbox.entity.outbox_event import OutboxEvent
from domain.shared.domain_exception import DomainException

logger = logging.getLogger(__name__)


class OutboxWorker:
    def __init__(
        self,
        producer: IProducer,
        outbox_repository: IOutboxRepository,
        datetime_provider : IDateTimeProvider,
        unit_of_work : IUnitOfWork
    ) -> None:
        self.running = False
        self.producer = producer
        self.outbox_repository = outbox_repository
        self.datetime_provider = datetime_provider
        self.unit_of_work = unit_of_work


    async def publish(self) -> None:
        self.running = True

        logger.info("Outbox worker started")

        while self.running:
            try:
                events: list[OutboxEvent] = (
                    await self.outbox_repository.get_unpublished()
                )

            except (ApplicationException, DomainException) as e:
                logger.exception(e.message)
                await asyncio.sleep(2)
                continue

            if not events:
                await asyncio.sleep(1)
                continue

            for event in events:
                if not self.running:
                    break

                try:
                    kafka_event = self._to_event(event)

                    await self.producer.produce(kafka_event)

                    event.mark_published(self.datetime_provider.now())
                    logger.info("published_at before update: %s", event.published_at)

                    await self.outbox_repository.update(event)
                    await self.unit_of_work.commit()

                    logger.info(
                        "Outbox event published: event_id=%s",
                        event.id,
                    )

                except Exception:
                    logger.exception(
                        "Failed to process outbox event: event_id=%s",
                        event.id
                    )

        logger.info("Outbox worker stopped")

    def stop(self) -> None:
        self.running = False

    @staticmethod
    def _to_event(event: OutboxEvent) -> KafkaEvent:
        return KafkaEvent(
            id=event.id,
            key=event.key,
            event_type=event.event_type,
            occurred_at=event.occurred_at,
            data=event.data,
            published_at=None,
        )
