from datetime import date

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

from analytics.config import settings

from analytics.domain.events.kafka_event import KafkaEvent
from analytics.domain.events.ticket_escalate_event import TicketEscalatedEvent

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


class TicketEscalatedHandler(IEventHandler):

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
        return "ticket.escalated"

    async def handle(self, event: KafkaEvent) -> None:

        payload = TicketEscalatedEvent.model_validate(event.data)

        # 1. Idempotency check.
        existing = (
            await self._ticket_activity_repository.get_by_source_event_id(
                event.id
            )
        )

        if existing is not None:
            return

        # 2. Retrieve ticket analytics.
        ticket = await self._ticket_analytics_repository.get_by_id(
            payload.ticket_id
        )

        if ticket is None:
            raise ValueError(
                f"Ticket analytics not found for ticket: {payload.ticket_id}"
            )

        # 3. Update ticket status.
        ticket.update_status(status=TicketStatus.ESCALATED)

        await self._ticket_analytics_repository.save(ticket)

        # 4. Record escalation activity.
        activity = TicketActivityEntity.create(
            activity_id=self._id_generator.generate_random_id(),
            source_event_id=event.id,
            ticket_id=payload.ticket_id,
            assignment_id=payload.new_assignment_id,
            actor_id=payload.actor_id,
            agent_id=payload.previous_agent_id,
            team_id=payload.previous_team_id,
            activity_type=TicketActivityType.ESCALATED.value,
            occurred_at=event.occurred_at,
        )

        await self._ticket_activity_repository.save(activity)

        # 5. Update previous agent performance metrics.
        if payload.previous_agent_id is not None:
            await self._update_performance_metric(
                dimension_type="AGENT",
                dimension_id=payload.previous_agent_id,
                metric_date=event.occurred_at.date(),
            )

        if payload.previous_team_id is not None:
            await self._update_performance_metric(
                dimension_type="TEAM",
                dimension_id=payload.previous_team_id,
                metric_date=event.occurred_at.date(),
            )

        score = AgentScoreEntity.create(
            score_id=self._id_generator.generate_random_id(),
            agent_id=payload.actor_id,
            ticket_id=payload.ticket_id,
            source_event_id=event.id,
            activity_type=TicketActivityType.ESCALATED.value,
            points=-abs(settings.ESCALATION_POINTS),
            occurred_at=event.occurred_at,
        )

        await self._agent_score_repository.save(score)


    async def _update_performance_metric(
        self,
        dimension_type: str,
        dimension_id: str,
        metric_date: date,
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

        metric.record_ticket_escalated()

        await self._performance_metric_repository.save(metric)
