from abc import ABC, abstractmethod

from analytics.application.performance_metric.dto.performance_metric_dto import (
    PerformanceMetricQueryDTO,
    PerformanceMetricSummaryResponseDTO,
    PerformanceMetricResponseDTO,
)


class IPerformanceMetricService(ABC):

    @abstractmethod
    async def get_metric(
        self,
        dimension_type: str,
        dimension_id: str,
    ) -> PerformanceMetricResponseDTO | None:
        pass

    @abstractmethod
    async def get_metrics_summary(
        self,
        dimension_type: str,
        dimension_id: str,    
    ) -> PerformanceMetricSummaryResponseDTO:
        pass
