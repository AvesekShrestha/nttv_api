from abc import ABC, abstractmethod
from datetime import datetime

from analytics.domain.analytics_event.analytics_event_aggregate import (
    AnalyticsEventAggregate,
)


class IAnalyticsEventService(ABC):

    @abstractmethod
    async def register_event(
        self,
        event_id: str,
        event_type: str,
        payload: dict,
    ) -> AnalyticsEventAggregate:
        """Register an incoming event if it does not already exist."""
        pass

    @abstractmethod
    async def claim_pending_events(
        self,
        limit: int = 100,
    ) -> list[AnalyticsEventAggregate]:
        """Atomically claim pending or retryable events for processing."""
        pass

    @abstractmethod
    async def mark_as_processed(
        self,
        event_id: str,
    ) -> None:
        pass

    @abstractmethod
    async def mark_as_failed(
        self,
        event_id: str,
        error: str,
    ) -> None:
        pass
