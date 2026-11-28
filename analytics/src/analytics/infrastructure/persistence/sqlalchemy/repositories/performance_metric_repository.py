from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from analytics.application.interfaces.performance_metric_repository_interface import (
    IPerformanceMetricRepository,
)
from analytics.domain.performance_mertic.entity.performance_matric_entity import (
    PerformanceMetricEntity,
)
from analytics.infrastructure.persistence.sqlalchemy.models.performance_metric_model import (
    PerformanceMetricModel,
)
from analytics.infrastructure.persistence.sqlalchemy.mappers.performance_metric_mapper import (
    PerformanceMetricMapper,
)
from analytics.application.shared.id_generator_interface import IIdGenerator


class PerformanceMetricRepository(IPerformanceMetricRepository):

    ALLOWED_METRIC_FIELDS = {
        "tickets_received",
        "tickets_acknowledged",
        "tickets_resolved",
        "tickets_forwarded",
        "tickets_escalated",
        "acknowledgment_sla_eligible",
        "acknowledgment_sla_breached",
        "resolution_sla_eligible",
        "resolution_sla_breached",
        "total_acknowledgment_seconds",
        "total_resolution_seconds",
    }

    ALLOWED_DIMENSION_TYPES = {
        "AGENT",
        "TEAM",
    }

    def __init__(
        self,
        session: AsyncSession,
        id_generator: IIdGenerator,
    ) -> None:
        self._session = session
        self._id_generator = id_generator

    async def save(
        self,
        metric: PerformanceMetricEntity,
    ) -> None:

        model = PerformanceMetricMapper.to_model(metric)

        await self._session.merge(model)
        await self._session.flush()

    async def get_by_dimension(
        self,
        dimension_type: str,
        dimension_id: str,
    ) -> PerformanceMetricEntity | None:

        stmt = select(PerformanceMetricModel).where(
            PerformanceMetricModel.dimension_type == dimension_type,
            PerformanceMetricModel.dimension_id == dimension_id,
        )

        result = await self._session.execute(stmt)

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return PerformanceMetricMapper.to_entity(model)

    async def increment_metrics(
        self,
        dimension_type: str,
        dimension_id: str,
        **increments: int,
    ) -> None:

        if dimension_type not in self.ALLOWED_DIMENSION_TYPES:
            raise ValueError(
                f"Invalid dimension type: {dimension_type}"
            )

        if not dimension_id:
            raise ValueError("Dimension ID cannot be empty")

        if not increments:
            raise ValueError("At least one metric increment is required")

        invalid_fields = (
            set(increments.keys()) - self.ALLOWED_METRIC_FIELDS
        )

        if invalid_fields:
            raise ValueError(
                f"Invalid metric fields: {', '.join(invalid_fields)}"
            )

        for field, value in increments.items():
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(
                    f"Metric increment for '{field}' must be an integer"
                )

            if value < 0:
                raise ValueError(
                    f"Metric increment for '{field}' cannot be negative"
                )

        stmt = insert(PerformanceMetricModel).values(
            id=self._id_generator.generate_random_id(),
            dimension_type=dimension_type,
            dimension_id=dimension_id,
            **increments,
        )

        stmt = stmt.on_conflict_do_update(
            constraint="uq_performance_dimension",
            set_={
                field: getattr(PerformanceMetricModel, field) + value
                for field, value in increments.items()
            },
        )

        await self._session.execute(stmt)
