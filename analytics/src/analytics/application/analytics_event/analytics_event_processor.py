import asyncio
import logging

from analytics.application.shared.application_exception import ApplicationException
from analytics.domain.events.kafka_event import KafkaEvent
from analytics.application.analytics_event.analytics_event_service_interface import (
    IAnalyticsEventService,
)
from analytics.application.dispatcher.dispatcher import EventDispatcher
from analytics.application.shared.unit_of_work_interface import IUnitOfWork
from analytics.domain.shared.domain_exception import DomainException

logger = logging.getLogger(__name__)


class EventProcessor:

    def __init__(
        self,
        analytics_event_service: IAnalyticsEventService,
        event_dispatcher: EventDispatcher,
        unit_of_work : IUnitOfWork,
        batch_size: int = 10,
        polling_interval: float = 2.0,
    ):
        self._analytics_event_service = analytics_event_service
        self._event_dispatcher = event_dispatcher
        self._batch_size = batch_size
        self._polling_interval = polling_interval
        self._running = False
        self.unit_of_work = unit_of_work

    async def start(self):
        self._running = True

        logger.info("Analytics event processor started")

        try:
            while self._running:

                events = await self._analytics_event_service.claim_pending_events(
                    limit=self._batch_size
                )

                if not events:
                    await asyncio.sleep(self._polling_interval)
                    continue

                for stored_event in events:

                    if not self._running:
                        break

                    await self._process_event(stored_event)

                await self.unit_of_work.commit()

        except (ApplicationException, DomainException) as e:
            logger.exception(e.message)

        finally:
            logger.info("Analytics event processor stopped")

    def stop(self):
        self._running = False

    async def _process_event(self, stored_event):

        try:
            event = KafkaEvent.model_validate(stored_event.payload)

            await self._event_dispatcher.dispatch(event)

            await self._analytics_event_service.mark_as_processed(
                event_id=stored_event.event_id
            )

            logger.info(
                "Successfully processed event: %s",
                stored_event.event_id,
            )

        except Exception as error:

            logger.exception(
                "Failed to process event: %s",
                stored_event.event_id,
            )

            await self._analytics_event_service.mark_as_failed(
                event_id=stored_event.event_id,
                error=str(error),
            )
