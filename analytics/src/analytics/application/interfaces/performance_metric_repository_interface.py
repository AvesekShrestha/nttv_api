from abc import ABC, abstractmethod

from analytics.domain.performance_mertic.entity.performance_matric_entity import (
    PerformanceMetricEntity,
)


class IPerformanceMetricRepository(ABC):

    @abstractmethod
    async def save(
        self,
        metric: PerformanceMetricEntity,
    ) -> None:
        pass

    @abstractmethod
    async def get_by_dimension(
        self,
        dimension_type: str,
        dimension_id: str,
    ) -> PerformanceMetricEntity | None:
        pass

    @abstractmethod
    async def increment_metrics(
        self,
        dimension_type: str,
        dimension_id: str,
        **increments: int,
    ) -> None:
        pass
