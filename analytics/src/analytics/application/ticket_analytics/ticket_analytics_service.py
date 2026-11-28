from datetime import datetime, timedelta

from analytics.application.ticket_analytics.dto.ticket_analytics_dto import (
    TicketAnalysisResponseDTO,
    TicketComparisonDTO,
)
from analytics.application.ticket_analytics.ticket_analytics_service_interface import (
    ITicketAnalyticsService,
)
from analytics.application.shared.unit_of_work_interface import IUnitOfWork

from analytics.domain.events.ticket_created_event import TicketCreatedEvent

from analytics.domain.ticket_analytics.entity.ticket_analytics_entity import (
    TicketAnalyticsEntity,
)
from analytics.domain.ticket_analytics.ticket_status import TicketStatus

from analytics.infrastructure.persistence.sqlalchemy.repositories.ticket_analytics_repository import (
    ITicketAnalyticsRepository,
)

from analytics.application.ticket_analytics.dto.ticket_analytics_query_dto import (
    TicketAnalyticsQueryDTO,
)


class TicketAnalyticsService(ITicketAnalyticsService):

    def __init__(
        self,
        ticket_analytics_repository: ITicketAnalyticsRepository,
        unit_of_work: IUnitOfWork,
    ):
        self._ticket_analytics_repository = ticket_analytics_repository
        self._unit_of_work = unit_of_work

    async def save(
        self,
        event_id: str,
        occurred_at: datetime,
        payload: TicketCreatedEvent,
    ) -> None:

        existing = await self._ticket_analytics_repository.get_by_id(
            payload.ticket_id
        )

        if existing is not None:
            return

        entity = TicketAnalyticsEntity.create(
            ticket_id=payload.ticket_id,
            category_id=payload.category_id,
            created_by=payload.created_by,
            priority=payload.priority,
            current_status=TicketStatus.NEW.value,
            created_at=occurred_at,
        )

        await self._ticket_analytics_repository.save(entity)
        await self._unit_of_work.commit()

    async def generate_analysis(
        self,
        query: TicketAnalyticsQueryDTO,
    ) -> TicketAnalysisResponseDTO:

        # Current-period analytics.
        summary = await self._ticket_analytics_repository.get_summary(
            query
        )

        distribution = (
            await self._ticket_analytics_repository.get_distribution(
                query
            )
        )

        trends = await self._ticket_analytics_repository.get_trends(
            query
        )

        # If no date range is provided, return all-time analytics.
        if query.start_date is None and query.end_date is None:

            comparison = TicketComparisonDTO(
                current_period_tickets=summary.total_tickets,
                previous_period_tickets=0,
                growth_percentage=0.0,
            )

        else:

            if query.start_date is None or query.end_date is None:
                raise ValueError(
                    "Both start_date and end_date must be provided together"
                )

            # Calculate the duration of the current period.
            period_days = (
                query.end_date - query.start_date
            ).days + 1

            # Calculate the immediately preceding period.
            previous_end_date = query.start_date - timedelta(days=1)

            previous_start_date = (
                previous_end_date - timedelta(days=period_days - 1)
            )

            previous_query = TicketAnalyticsQueryDTO(
                start_date=previous_start_date,
                end_date=previous_end_date,
            )

            previous_summary = (
                await self._ticket_analytics_repository.get_summary(
                    previous_query
                )
            )

            previous_period_tickets = (
                previous_summary.total_tickets
            )

            current_period_tickets = summary.total_tickets

            # Calculate percentage growth.
            growth_percentage = (
                (
                    current_period_tickets - previous_period_tickets
                )
                / previous_period_tickets
                * 100
                if previous_period_tickets > 0
                else 0.0
            )

            comparison = TicketComparisonDTO(
                current_period_tickets=current_period_tickets,
                previous_period_tickets=previous_period_tickets,
                growth_percentage=round(growth_percentage, 2),
            )

        return TicketAnalysisResponseDTO(
            start_date=query.start_date,
            end_date=query.end_date,
            summary=summary,
            distribution=distribution,
            trends=trends,
            comparison=comparison,
        )
