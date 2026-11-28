from datetime import date

from analytics.application.exceptions import MissingRequiredAttributeException
from analytics.application.interfaces.agent_score_repository_interface import (
    IAgentScoreRepository,
)
from analytics.application.interfaces.performance_metric_repository_interface import (
    IPerformanceMetricRepository,
)
from analytics.application.interfaces.ticket_activity_repository_interface import (
    ITicketActivityRepository,
)
from analytics.application.interfaces.ticket_analytics_repository_interface import (
    ITicketAnalyticsRepository,
)
from analytics.application.shared.event_handler_interface import IEventHandler
from analytics.application.shared.id_generator_interface import IIdGenerator

from analytics.domain.events.kafka_event import KafkaEvent
from analytics.domain.events.ticket_acknowledge_event import (
    TicketAcknowledgedEvent,
)

from analytics.domain.ticket_activity.entity.ticket_activity_entity import (
    TicketActivityEntity,
)
from analytics.domain.ticket_activity.ticket_activity import TicketActivityType

from analytics.domain.ticket_analytics.ticket_status import TicketStatus
from analytics.domain.performance_mertic.entity.performance_matric_entity import PerformanceMetricEntity

from analytics.domain.agent_score.entity.agent_score_entity import (
    AgentScoreEntity,
)

from analytics.config import settings


class TicketAcknowledgedHandler(IEventHandler):

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
        return "ticket.acknowledged"

    async def handle(self, event: KafkaEvent) -> None:

        payload = TicketAcknowledgedEvent.model_validate(event.data)

        # 1. Idempotency check.
        existing = (
            await self._ticket_activity_repository.get_by_source_event_id(
                event.id
            )
        )

        if existing is not None:
            return

        # 2. Calculate acknowledgment duration.
        acknowledgment_seconds = int(
            (event.occurred_at - payload.assigned_at).total_seconds()
        )

        if acknowledgment_seconds < 0:
            raise ValueError(
                "Acknowledgment time cannot be earlier than assignment time."
            )

        # 3. Calculate SLA result.
        acknowledgment_sla_breached = (
            event.occurred_at > payload.acknowledgment_sla_deadline
        )

        # 4. Retrieve ticket analytics.
        ticket = await self._ticket_analytics_repository.get_by_id(
            payload.ticket_id
        )

        if ticket is None:
            raise ValueError(
                f"Ticket analytics not found for ticket: {payload.ticket_id}"
            )

        # 5. Update ticket status.
        ticket.update_status(status=TicketStatus.INPROCESS)

        await self._ticket_analytics_repository.save(ticket)

        # 6. Record ticket activity.
        activity = TicketActivityEntity.create(
            activity_id=self._id_generator.generate_random_id(),
            source_event_id=event.id,
            ticket_id=payload.ticket_id,
            assignment_id=payload.assignment_id,
            actor_id=payload.actor_id,
            agent_id=payload.agent_id,
            team_id=payload.team_id,
            activity_type=TicketActivityType.ACKNOWLEDGED.value,
            occurred_at=event.occurred_at,
        )

        await self._ticket_activity_repository.save(activity)

        # 7. Update agent performance metrics.
        await self._update_performance_metric(
            dimension_type="AGENT",
            dimension_id=payload.agent_id,
            metric_date=event.occurred_at.date(),
            acknowledgment_seconds=acknowledgment_seconds,
            sla_breached=acknowledgment_sla_breached,
        )

        # 8. Update team performance metrics.
        await self._update_performance_metric(
            dimension_type="TEAM",
            dimension_id=payload.team_id,
            metric_date=event.occurred_at.date(),
            acknowledgment_seconds=acknowledgment_seconds,
            sla_breached=acknowledgment_sla_breached,
        )

        # 9. Record agent score.
        score = AgentScoreEntity.create(
            score_id=self._id_generator.generate_random_id(),
            agent_id=payload.agent_id,
            ticket_id=payload.ticket_id,
            source_event_id=event.id,
            activity_type=TicketActivityType.ACKNOWLEDGED.value,
            points=settings.ACKNOWLEDGEMENT_POINTS,
            occurred_at=event.occurred_at,
        )

        await self._agent_score_repository.save(score)


    async def _update_performance_metric(
        self,
        dimension_type: str,
        dimension_id: str | None,
        metric_date: date,
        acknowledgment_seconds: int,
        sla_breached: bool,
    ) -> None:

        if dimension_id is None:
            raise MissingRequiredAttributeException(
                f"{dimension_type.lower()}_id is required "
                f"to update acknowledgment performance metrics"
            )

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

        metric.record_ticket_acknowledged(
            acknowledgment_seconds=acknowledgment_seconds,
            sla_breached=sla_breached,
        )

        await self._performance_metric_repository.save(metric)
