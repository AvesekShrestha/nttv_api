from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import Date, case, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from analytics.application.ticket_analytics.dto.ticket_analytics_query_dto import (
    TicketAnalyticsQueryDTO,
)
from analytics.application.ticket_analytics.dto.ticket_analytics_dto import (
    TicketDistributionDTO,
    TicketSummaryDTO,
    TicketTrendDTO,
)
from analytics.application.interfaces.ticket_analytics_repository_interface import (
    ITicketAnalyticsRepository,
)
from analytics.domain.ticket_analytics.entity.ticket_analytics_entity import (
    TicketAnalyticsEntity,
)
from analytics.infrastructure.persistence.sqlalchemy.mappers.ticket_analytics_mapper import (
    TicketAnalyticsMapper,
)
from analytics.infrastructure.persistence.sqlalchemy.models.ticket_analytics_model import (
    TicketAnalyticsModel,
)


class TicketAnalyticsRepository(ITicketAnalyticsRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, entity: TicketAnalyticsEntity) -> None:
        model = TicketAnalyticsMapper.to_model(entity)

        await self._session.merge(model)
        await self._session.flush()

    async def get_by_id(
        self,
        ticket_id: str,
    ) -> TicketAnalyticsEntity | None:

        statement = select(TicketAnalyticsModel).where(
            TicketAnalyticsModel.ticket_id == ticket_id
        )

        result = await self._session.execute(statement)

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return TicketAnalyticsMapper.to_domain(model)

    async def exists(self, ticket_id: str) -> bool:

        statement = select(TicketAnalyticsModel.ticket_id).where(
            TicketAnalyticsModel.ticket_id == ticket_id
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none() is not None

    @staticmethod
    def _get_date_range(
        query: TicketAnalyticsQueryDTO,
    ) -> tuple[datetime | None, datetime | None]:

        if query.start_date is None or query.end_date is None:
            return None, None

        start_datetime = datetime.combine(
            query.start_date,
            time.min,
            tzinfo=timezone.utc,
        )

        end_datetime = datetime.combine(
            query.end_date + timedelta(days=1),
            time.min,
            tzinfo=timezone.utc,
        )

        return start_datetime, end_datetime

    @staticmethod
    def _get_utc_date_expression(column):
        return cast(func.timezone("UTC", column), Date)

    @staticmethod
    def _to_utc_datetime(value: datetime) -> datetime:

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

    async def get_summary(
        self,
        query: TicketAnalyticsQueryDTO,
    ) -> TicketSummaryDTO:

        start_datetime, end_datetime = self._get_date_range(query)

        filters: list[ColumnElement[bool]] = []

        if start_datetime is not None and end_datetime is not None:
            filters.extend(
                [
                    TicketAnalyticsModel.created_at >= start_datetime,
                    TicketAnalyticsModel.created_at < end_datetime,
                ]
            )

        statement = (
            select(
                func.count(
                    TicketAnalyticsModel.ticket_id
                ).label("total_tickets"),

                func.count(
                    case(
                        (
                            TicketAnalyticsModel.resolved_at.is_not(None),
                            1,
                        )
                    )
                ).label("resolved_tickets"),

                func.count(
                    case(
                        (
                            TicketAnalyticsModel.resolved_at.is_(None),
                            1,
                        )
                    )
                ).label("unresolved_tickets"),

                func.avg(
                    TicketAnalyticsModel.resolution_duration_seconds
                ).label("average_resolution_seconds"),
            )
            .where(*filters)
        )

        result = await self._session.execute(statement)

        row = result.one()

        total_tickets = row.total_tickets or 0
        resolved_tickets = row.resolved_tickets or 0
        unresolved_tickets = row.unresolved_tickets or 0

        average_resolution_seconds = (
            float(row.average_resolution_seconds)
            if row.average_resolution_seconds is not None
            else 0.0
        )

        resolution_rate = (
            (resolved_tickets / total_tickets) * 100
            if total_tickets > 0
            else 0.0
        )

        return TicketSummaryDTO(
            total_tickets=total_tickets,
            resolved_tickets=resolved_tickets,
            unresolved_tickets=unresolved_tickets,
            resolution_rate=round(resolution_rate, 2),
            average_resolution_seconds=round(
                average_resolution_seconds,
                2,
            ),
        )

    async def get_distribution(
        self,
        query: TicketAnalyticsQueryDTO,
    ) -> TicketDistributionDTO:

        start_datetime, end_datetime = self._get_date_range(query)

        filters: list[ColumnElement[bool]] = []

        if start_datetime is not None and end_datetime is not None:
            filters.extend(
                [
                    TicketAnalyticsModel.created_at >= start_datetime,
                    TicketAnalyticsModel.created_at < end_datetime,
                ]
            )

        status_statement = (
            select(
                TicketAnalyticsModel.current_status,
                func.count(TicketAnalyticsModel.ticket_id),
            )
            .where(*filters)
            .group_by(TicketAnalyticsModel.current_status)
        )

        status_result = await self._session.execute(status_statement)

        by_status = {
            status: count
            for status, count in status_result.all()
        }

        priority_statement = (
            select(
                TicketAnalyticsModel.priority,
                func.count(TicketAnalyticsModel.ticket_id),
            )
            .where(*filters)
            .group_by(TicketAnalyticsModel.priority)
        )

        priority_result = await self._session.execute(
            priority_statement
        )

        by_priority = {
            priority: count
            for priority, count in priority_result.all()
        }

        category_statement = (
            select(
                TicketAnalyticsModel.category_id,
                func.count(TicketAnalyticsModel.ticket_id),
            )
            .where(*filters)
            .group_by(TicketAnalyticsModel.category_id)
        )

        category_result = await self._session.execute(
            category_statement
        )

        by_category = {
            category_id: count
            for category_id, count in category_result.all()
        }

        return TicketDistributionDTO(
            by_status=by_status,
            by_priority=by_priority,
            by_category=by_category,
        )

    async def get_trends(
        self,
        query: TicketAnalyticsQueryDTO,
    ) -> list[TicketTrendDTO]:

        start_datetime, end_datetime = self._get_date_range(query)

        # Determine the date range for the trends.
        if start_datetime is None and end_datetime is None:

            date_range_statement = select(
                func.min(
                    TicketAnalyticsModel.created_at
                ).label("first_created"),

                func.max(
                    TicketAnalyticsModel.created_at
                ).label("last_created"),

                func.max(
                    TicketAnalyticsModel.resolved_at
                ).label("last_resolved"),
            )

            date_range_result = await self._session.execute(
                date_range_statement
            )

            date_range = date_range_result.one()

            if date_range.first_created is None:
                return []

            first_created = self._to_utc_datetime(
                date_range.first_created
            )

            last_created = self._to_utc_datetime(
                date_range.last_created
            )

            last_trend_timestamp = last_created

            if date_range.last_resolved is not None:

                last_resolved = self._to_utc_datetime(
                    date_range.last_resolved
                )

                if last_resolved > last_trend_timestamp:
                    last_trend_timestamp = last_resolved

            first_trend_date: date = first_created.date()
            last_trend_date: date = last_trend_timestamp.date()

        else:

            if query.start_date is None or query.end_date is None:
                raise ValueError(
                    "Both start_date and end_date must be provided together"
                )

            first_trend_date: date = query.start_date
            last_trend_date: date = query.end_date

        trends: dict[date, dict[str, int]] = {}

        current_date: date = first_trend_date

        while current_date <= last_trend_date:

            trends[current_date] = {
                "created": 0,
                "resolved": 0,
            }

            current_date += timedelta(days=1)

        # Created ticket trends.
        created_date = self._get_utc_date_expression(
            TicketAnalyticsModel.created_at
        )

        created_filters: list[ColumnElement[bool]] = []

        if start_datetime is not None and end_datetime is not None:
            created_filters.extend(
                [
                    TicketAnalyticsModel.created_at >= start_datetime,
                    TicketAnalyticsModel.created_at < end_datetime,
                ]
            )

        created_statement = (
            select(
                created_date.label("trend_date"),
                func.count(
                    TicketAnalyticsModel.ticket_id
                ).label("ticket_count"),
            )
            .where(*created_filters)
            .group_by(created_date)
            .order_by(created_date)
        )

        created_result = await self._session.execute(
            created_statement
        )

        for trend_date, count in created_result.all():

            if trend_date in trends:
                trends[trend_date]["created"] = count

        # Resolved ticket trends.
        resolved_date = self._get_utc_date_expression(
            TicketAnalyticsModel.resolved_at
        )

        resolved_filters: list[ColumnElement[bool]] = [
            TicketAnalyticsModel.resolved_at.is_not(None),
        ]

        if start_datetime is not None and end_datetime is not None:
            resolved_filters.extend(
                [
                    TicketAnalyticsModel.resolved_at >= start_datetime,
                    TicketAnalyticsModel.resolved_at < end_datetime,
                ]
            )

        resolved_statement = (
            select(
                resolved_date.label("trend_date"),
                func.count(
                    TicketAnalyticsModel.ticket_id
                ).label("ticket_count"),
            )
            .where(*resolved_filters)
            .group_by(resolved_date)
            .order_by(resolved_date)
        )

        resolved_result = await self._session.execute(
            resolved_statement
        )

        for trend_date, count in resolved_result.all():

            if trend_date in trends:
                trends[trend_date]["resolved"] = count

        return [
            TicketTrendDTO(
                date=trend_date,
                created=values["created"],
                resolved=values["resolved"],
            )
            for trend_date, values in sorted(trends.items())
        ]
