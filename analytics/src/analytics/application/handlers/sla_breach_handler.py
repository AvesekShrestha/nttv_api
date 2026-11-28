from pydantic import ValidationError
from analytics.application.exceptions import MissingRequiredAttributeException
from analytics.application.shared.event_handler_interface import IEventHandler
from analytics.domain.events.kafka_event import KafkaEvent
from analytics.domain.events.sla_breach_event import SLABreachedEvent

from analytics.application.interfaces.ticket_activity_repository_interface import (
    ITicketActivityRepository,
)
from analytics.application.interfaces.performance_metric_repository_interface import (
    IPerformanceMetricRepository,
)
from analytics.application.interfaces.agent_score_repository_interface import (
    IAgentScoreRepository,
)
from analytics.application.shared.id_generator_interface import IIdGenerator

from analytics.domain.ticket_activity.entity.ticket_activity_entity import (
    TicketActivityEntity,
)
from analytics.domain.ticket_activity.ticket_activity import TicketActivityType
from analytics.domain.performance_mertic.entity.performance_matric_entity import (
    PerformanceMetricEntity,
)
from analytics.domain.agent_score.entity.agent_score_entity import (
    AgentScoreEntity,
)

from analytics.config import settings


class SLABreachedHandler(IEventHandler):
    def __init__(
        self,
        ticket_activity_repository: ITicketActivityRepository,
        performance_metric_repository: IPerformanceMetricRepository,
        agent_score_repository: IAgentScoreRepository,
        id_generator: IIdGenerator,
    ):
        self._ticket_activity_repository = ticket_activity_repository
        self._performance_metric_repository = performance_metric_repository
        self._agent_score_repository = agent_score_repository
        self._id_generator = id_generator

    @property
    def event_type(self) -> str:
        return "ticket.breached"

    async def handle(self, event: KafkaEvent[dict]) -> None:
        try:
            payload = SLABreachedEvent.model_validate(event.data)
        except ValidationError as e:
            raise MissingRequiredAttributeException(
                f"Required attribute is missing or null in ticket.sla_breached event: {e}"
            )

        # 1. Idempotency check
        existing_activity = (
            await self._ticket_activity_repository.get_by_source_event_id(event.id)
        )

        if existing_activity is not None:
            return

        # 2. Create SLA breach activity
        activity = TicketActivityEntity.create(
            activity_id=self._id_generator.generate_random_id(),
            source_event_id=event.id,
            ticket_id=payload.ticket_id,
            assignment_id=payload.assignment_id,
            actor_id=None,
            agent_id=payload.agent_id,
            team_id=payload.team_id,
            activity_type=TicketActivityType.SLA_BREACHED,
            occurred_at=event.occurred_at,
        )

        await self._ticket_activity_repository.save(activity)

        metric_date = payload.deadline_at

        if payload.agent_id is not None:
            await self._update_performance_metric(
                dimension_type="AGENT",
                dimension_id=payload.agent_id,
                metric_date=metric_date,
                sla_type=payload.sla_type,
            )

        if payload.team_id is not None:
            await self._update_performance_metric(
                dimension_type="TEAM",
                dimension_id=payload.team_id,
                metric_date=metric_date,
                sla_type=payload.sla_type,
            )

        if payload.sla_type == "RESOLUTION" and payload.agent_id is not None:
            await self._deduct_resolution_sla_points(
                event=event,
                payload=payload,
            )

    async def _update_performance_metric(
        self,
        dimension_type: str,
        dimension_id: str,
        metric_date,
        sla_type: str,
    ) -> None:
        metric = await self._performance_metric_repository.get_by_dimension(
            dimension_type=dimension_type,
            dimension_id=dimension_id,
        )

        if metric is None:
            metric = PerformanceMetricEntity.create(
                metric_id=self._id_generator.generate_random_id(),
                dimension_type=dimension_type,
                dimension_id=dimension_id,
            )

        if sla_type == "ACKNOWLEDGMENT":
            metric.record_acknowledgment_sla_breach()

        elif sla_type == "RESOLUTION":
            metric.record_resolution_sla_breach()

        await self._performance_metric_repository.save(metric)

    async def _deduct_resolution_sla_points(
        self,
        event: KafkaEvent[dict],
        payload: SLABreachedEvent,
    ) -> None:
        if payload.agent_id is None:
            return

        penalty_points = -abs(settings.RESOLUTION_SLA_BREACH_POINTS)

        score = AgentScoreEntity.create(
            score_id=self._id_generator.generate_random_id(),
            agent_id=payload.agent_id,
            ticket_id=payload.ticket_id,
            source_event_id=event.id,
            activity_type=TicketActivityType.SLA_BREACHED,
            points=penalty_points,
            occurred_at=event.occurred_at,
        )

        await self._agent_score_repository.save(score)
