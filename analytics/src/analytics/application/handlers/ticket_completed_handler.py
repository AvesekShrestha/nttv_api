from analytics.domain.events.kafka_event import KafkaEvent
from analytics.domain.events.ticket_complete_event import (
    TicketCompletedEvent,
)

from analytics.application.interfaces.ticket_activity_repository_interface import (
    ITicketActivityRepository,
)
from analytics.application.interfaces.ticket_analytics_repository_interface import (
    ITicketAnalyticsRepository,
)
from analytics.application.interfaces.performance_metric_repository_interface import (
    IPerformanceMetricRepository,
)
from analytics.application.interfaces.agent_score_repository_interface import (
    IAgentScoreRepository,
)
from analytics.application.shared.id_generator_interface import IIdGenerator
from analytics.application.exceptions import MissingRequiredAttributeException
from analytics.domain.ticket_activity.entity.ticket_activity_entity import (
    TicketActivityEntity,
)
from analytics.domain.ticket_activity.ticket_activity import TicketActivityType
from analytics.domain.ticket_analytics.ticket_status import TicketStatus
from analytics.domain.performance_mertic.entity.performance_matric_entity import (
    PerformanceMetricEntity,
)
from analytics.domain.agent_score.entity.agent_score_entity import (
    AgentScoreEntity,
)

from analytics.config import settings


class TicketCompletedHandler:
    def __init__(
        self,
        ticket_activity_repository: ITicketActivityRepository,
        ticket_analytics_repository: ITicketAnalyticsRepository,
        performance_metric_repository: IPerformanceMetricRepository,
        agent_score_repository: IAgentScoreRepository,
        id_generator: IIdGenerator,
    ):
        self._ticket_activity_repository = ticket_activity_repository
        self._ticket_analytics_repository = ticket_analytics_repository
        self._performance_metric_repository = performance_metric_repository
        self._agent_score_repository = agent_score_repository
        self._id_generator = id_generator

    @property
    def event_type(self) -> str:
        return "ticket.completed"

    async def handle(self, event: KafkaEvent[dict]) -> None:
        payload = TicketCompletedEvent.model_validate(event.data)

        # 1. Validate required attributes
        if payload.team_id is None:
            raise MissingRequiredAttributeException(
                f"team_id is missing in ticket.completed event "
                f"for ticket: {payload.ticket_id}"
            )

        if payload.resolution_sla_deadline is None:
            raise MissingRequiredAttributeException(
                f"resolution_sla_deadline is missing in ticket.completed event "
                f"for ticket: {payload.ticket_id}"
            )

        # 2. Idempotency check
        existing_activity = (
            await self._ticket_activity_repository.get_by_source_event_id(
                event.id
            )
        )

        if existing_activity is not None:
            return

        # 3. Retrieve ticket analytics
        ticket = await self._ticket_analytics_repository.get_by_id(
            payload.ticket_id
        )

        if ticket is None:
            raise ValueError(
                f"Ticket analytics not found: {payload.ticket_id}"
            )

        # 4. Calculate resolution duration
        resolution_seconds = int(
            (event.occurred_at - ticket.created_at).total_seconds()
        )

        if resolution_seconds < 0:
            raise ValueError("Resolution time cannot be negative")

        # 5. Check resolution SLA
        resolution_sla_breached = (
            event.occurred_at > payload.resolution_sla_deadline
        )

        # 6. Update ticket analytics
        ticket.update_status(TicketStatus.COMPLETED)
        ticket.update_resolution_duration_seconds(resolution_seconds)

        await self._ticket_analytics_repository.save(ticket)

        # 7. Record completion activity
        activity = TicketActivityEntity.create(
            activity_id=self._id_generator.generate_random_id(),
            source_event_id=event.id,
            ticket_id=payload.ticket_id,
            assignment_id=payload.assignment_id,
            actor_id=payload.actor_id,
            agent_id=payload.agent_id,
            team_id=payload.team_id,
            activity_type=TicketActivityType.COMPLETED,
            occurred_at=event.occurred_at,
        )

        await self._ticket_activity_repository.save(activity)

        # 8. Update agent performance metrics
        await self._update_performance_metric(
            dimension_type="AGENT",
            dimension_id=payload.agent_id,
            metric_date=event.occurred_at.date(),
            resolution_seconds=resolution_seconds,
            sla_breached=resolution_sla_breached,
        )

        # 9. Update team performance metrics
        await self._update_performance_metric(
            dimension_type="TEAM",
            dimension_id=payload.team_id,
            metric_date=event.occurred_at.date(),
            resolution_seconds=resolution_seconds,
            sla_breached=resolution_sla_breached,
        )

        # 10. Award resolution points
        await self._award_resolution_points(
            event=event,
            payload=payload,
        )

        # 11. Commit all changes

    async def _update_performance_metric(
        self,
        dimension_type: str,
        dimension_id: str,
        metric_date,
        resolution_seconds: int,
        sla_breached: bool,
    ) -> None:
        metric = (
            await self._performance_metric_repository.get_by_dimension(
                dimension_type=dimension_type,
                dimension_id=dimension_id,
            )
        )

        if metric is None:
            metric = PerformanceMetricEntity.create(
                metric_id=self._id_generator.generate_random_id(),
                dimension_type=dimension_type,
                dimension_id=dimension_id,
            )

        metric.record_ticket_resolved(
            resolution_seconds=resolution_seconds,
            sla_breached=sla_breached,
        )

        await self._performance_metric_repository.save(metric)

    async def _award_resolution_points(
        self,
        event: KafkaEvent[dict],
        payload: TicketCompletedEvent,
    ) -> None:
        score = AgentScoreEntity.create(
            score_id=self._id_generator.generate_random_id(),
            agent_id=payload.agent_id,
            ticket_id=payload.ticket_id,
            source_event_id=event.id,
            activity_type=TicketActivityType.COMPLETED,
            points=abs(settings.RESOLUTION_POINTS),
            occurred_at=event.occurred_at,
        )

        await self._agent_score_repository.save(score)

