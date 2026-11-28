from datetime import timedelta

from analytics.config import settings
from analytics.domain.analytics_event.analytics_event_aggregate import (
    AnalyticsEventAggregate,
)
from analytics.application.analytics_event.analytics_event_service_interface import (
    IAnalyticsEventService,
)
from analytics.application.interfaces.analytics_repository_interface import (
    IAnalyticsEventRepository,
)
from analytics.application.shared.id_generator_interface import (
    IIdGenerator,
)
from analytics.application.shared.datetime_provider_interface import (
    IDateTimeProvider,
)
from analytics.application.shared.unit_of_work_interface import (
    IUnitOfWork,
)


class AnalyticsEventService(IAnalyticsEventService):

    def __init__(
        self,
        analytics_event_repository: IAnalyticsEventRepository,
        id_generator: IIdGenerator,
        datetime_provider: IDateTimeProvider,
        unit_of_work: IUnitOfWork,
    ):
        self._analytics_event_repository = analytics_event_repository
        self._id_generator = id_generator
        self._datetime_provider = datetime_provider
        self._unit_of_work = unit_of_work

    async def register_event(
        self,
        event_id: str,
        event_type: str,
        payload: dict,
    ) -> AnalyticsEventAggregate:

        event = AnalyticsEventAggregate.create(
            id=self._id_generator.generate_random_id(),
            event_id=event_id,
            event_type=event_type,
            payload=payload,
        )

        inserted = await self._analytics_event_repository.add_if_not_exists(
            event
        )

        if inserted:
            await self._unit_of_work.commit()
            return event

        existing_event = (
            await self._analytics_event_repository.get_by_event_id(
                event_id
            )
        )

        if existing_event is None:
            raise RuntimeError(
                f"Failed to retrieve registered event: {event_id}"
            )

        return existing_event

    async def claim_pending_events(
        self,
        limit: int = 100,
    ) -> list[AnalyticsEventAggregate]:

        events = await self._analytics_event_repository.claim_pending_events(
            limit=limit,
            now=self._datetime_provider.now(),
        )

        if events:
            await self._unit_of_work.commit()

        return events

    async def mark_as_processed(
        self,
        event_id: str,
    ) -> None:

        event = await self._get_event(event_id)

        event.mark_as_processed(
            self._datetime_provider.now()
        )

        await self._analytics_event_repository.save(event)
        await self._unit_of_work.commit()

    async def mark_as_failed(
        self,
        event_id: str,
        error: str,
    ) -> None:

        event = await self._get_event(event_id)

        next_retry_at = None

        if event.attempts < settings.MAX_RETRY_ATTEMPTS:
            delay = self._calculate_retry_delay(event.attempts)

            next_retry_at = (
                self._datetime_provider.now()
                + timedelta(seconds=delay)
            )

        event.mark_as_failed(
            error=error,
            next_retry_at=next_retry_at,
        )

        await self._analytics_event_repository.save(event)
        await self._unit_of_work.commit()

    @staticmethod
    def _calculate_retry_delay(attempts: int) -> int:

        delays = [5, 30, 120, 600]

        return delays[min(max(attempts - 1, 0), len(delays) - 1)]

    async def _get_event(
        self,
        event_id: str,
    ) -> AnalyticsEventAggregate:

        event = await self._analytics_event_repository.get_by_event_id(
            event_id
        )

        if event is None:
            raise ValueError(
                f"Analytics event not found: {event_id}"
            )

        return event

