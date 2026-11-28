from abc import ABC, abstractmethod
from datetime import datetime

from analytics.domain.analytics_event.analytics_event_aggregate import (
    AnalyticsEventAggregate,
)


class IAnalyticsEventRepository(ABC):

    @abstractmethod
    async def get_by_event_id(
        self,
        event_id: str,
    ) -> AnalyticsEventAggregate | None:
        pass

    @abstractmethod
    async def add_if_not_exists(
        self,
        event: AnalyticsEventAggregate,
    ) -> bool:
        pass

    @abstractmethod
    async def claim_pending_events(
        self,
        limit: int,
        now: datetime,
    ) -> list[AnalyticsEventAggregate]:
        pass

    @abstractmethod
    async def save(
        self,
        event: AnalyticsEventAggregate,
    ) -> None:
        pass
