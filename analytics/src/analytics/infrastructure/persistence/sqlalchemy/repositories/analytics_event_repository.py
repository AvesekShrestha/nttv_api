from datetime import datetime

from sqlalchemy import select, or_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from analytics.domain.analytics_event.analytics_event_aggregate import (
    AnalyticsEventAggregate,
)
from analytics.application.interfaces.analytics_repository_interface import (
    IAnalyticsEventRepository,
)
from analytics.infrastructure.persistence.sqlalchemy.mappers.analytics_mapper import (
    AnalyticsEventMapper,
)
from analytics.infrastructure.persistence.sqlalchemy.models.analytics_event_model import (
    AnalyticsEventModel,
)


class AnalyticsEventRepository(IAnalyticsEventRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_event_id(
        self,
        event_id: str,
    ) -> AnalyticsEventAggregate | None:

        query = select(AnalyticsEventModel).where(
            AnalyticsEventModel.event_id == event_id
        )

        result = await self._session.execute(query)

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return AnalyticsEventMapper.to_domain(model)

    async def add_if_not_exists(
        self,
        event: AnalyticsEventAggregate,
    ) -> bool:

        model = AnalyticsEventMapper.to_model(event)

        statement = (
            insert(AnalyticsEventModel)
            .values(
                id=model.id,
                event_id=model.event_id,
                event_type=model.event_type,
                payload=model.payload,
                status=model.status,
                attempts=model.attempts,
                last_error=model.last_error,
                next_retry_at=model.next_retry_at,
                created_at=model.created_at,
                processed_at=model.processed_at,
            )
            .on_conflict_do_nothing(
                index_elements=["event_id"]
            )
            .returning(AnalyticsEventModel.id)
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none() is not None

    async def claim_pending_events(
        self,
        limit: int,
        now: datetime,
    ) -> list[AnalyticsEventAggregate]:

        eligible_conditions = or_(
            AnalyticsEventModel.status == "PENDING",
            (
                (AnalyticsEventModel.status == "FAILED")
                & (AnalyticsEventModel.next_retry_at <= now)
            ),
        )

        query = (
            select(AnalyticsEventModel)
            .where(eligible_conditions)
            .order_by(AnalyticsEventModel.created_at.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        result = await self._session.execute(query)

        models = result.scalars().all()

        events = []

        for model in models:
            model.status = "PROCESSING"
            model.attempts += 1
            model.last_error = None
            model.next_retry_at = None

            events.append(
                AnalyticsEventMapper.to_domain(model)
            )

        await self._session.flush()

        return events

    async def save(
        self,
        event: AnalyticsEventAggregate,
    ) -> None:

        model = AnalyticsEventMapper.to_model(event)

        await self._session.merge(model)

        await self._session.flush()

