from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector import containers, providers

from analytics.application import dispatcher
from analytics.application.analytics_event.analytics_event_processor import EventProcessor
from analytics.application.analytics_event.analytics_event_service import AnalyticsEventService
from analytics.application.ticket_activity.ticket_activity_service import TicketActivityService
from analytics.application.ticket_analytics.ticket_analytics_service import (
    TicketAnalyticsService,
)
from analytics.application.performance_metric.performance_metric_service import (
    PerformanceMetricService,
)
from analytics.application.agent_score.agent_score_service import AgentScoreService
from analytics.application.dashboard.dashboard_service import DashboardService
from analytics.infrastructure.messaging.kafka.consumer import EventIngestion
from analytics.infrastructure.persistence.sqlalchemy.repositories.analytics_event_repository import (
    AnalyticsEventRepository,
)
from analytics.infrastructure.persistence.sqlalchemy.repositories.ticket_analytics_repository import (
    TicketAnalyticsRepository,
)
from analytics.infrastructure.persistence.sqlalchemy.repositories.ticket_activity_repository import (
    TicketActivityRepository,
)
from analytics.infrastructure.persistence.sqlalchemy.repositories.performance_metric_repository import (
    PerformanceMetricRepository,
)
from analytics.infrastructure.persistence.sqlalchemy.repositories.agent_score_repository import (
    AgentScoreRepository,
)
from analytics.infrastructure.identity.id_generator import IdGenerator
from analytics.infrastructure.identity.datetime_provider import DateTimeProvider
from analytics.infrastructure.persistence.sqlalchemy.unit_of_work import UnitOfWork

from analytics.application.handlers.ticket_created_handler import TicketCreatedHandler
from analytics.application.handlers.ticket_dispatch_handler import (
    TicketDispatchedHandler,
)
from analytics.application.handlers.ticket_acknowledge_handler import (
    TicketAcknowledgedHandler,
)
from analytics.application.handlers.ticket_forward_handler import TicketForwardedHandler
from analytics.application.handlers.ticket_escalate_handler import (
    TicketEscalatedHandler,
)
from analytics.application.handlers.ticket_completed_handler import (
    TicketCompletedHandler,
)
from analytics.application.handlers.sla_breach_handler import SLABreachedHandler
from analytics.application.dispatcher.dispatcher import EventDispatcher
from analytics.application.ticket_analytics.ticket_analytics_service import TicketAnalyticsService


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    session = providers.Dependency(instance_of=AsyncSession)

    id_generator = providers.Singleton(IdGenerator)

    datetime_provider = providers.Singleton(DateTimeProvider)
    unit_of_work = providers.Singleton(UnitOfWork, session=session)

    analytics_event_repository = providers.Factory(
        AnalyticsEventRepository, session=session
    )

    ticket_analytics_repository = providers.Factory(
        TicketAnalyticsRepository, session=session
    )

    ticket_activity_repository = providers.Factory(
        TicketActivityRepository, session=session
    )

    performance_metric_repository = providers.Factory(
        PerformanceMetricRepository, session=session, id_generator=id_generator
    )

    agent_score_repository = providers.Factory(AgentScoreRepository, session=session)

    dashboard_service = providers.Factory(
        DashboardService,
        ticket_analytics_repository=ticket_analytics_repository,
        agent_score_repository=agent_score_repository,
        performance_metric_repository=performance_metric_repository,
    )

    ticket_analytics_service = providers.Factory(
        TicketAnalyticsService,
        ticket_analytics_repository=ticket_analytics_repository,
        unit_of_work=unit_of_work,
    )

    performance_metric_service = providers.Factory(
        PerformanceMetricService,
        performance_metric_repository=performance_metric_repository,
    )

    agent_score_service = providers.Factory(
        AgentScoreService,
        agent_score_repository=agent_score_repository,
    )

    ticket_activity_service = providers.Factory(
        TicketActivityService,
        ticket_activity_repository=ticket_activity_repository,
    )

    ticket_created_handler = providers.Factory(
        TicketCreatedHandler,
        ticket_analytics_repository=ticket_analytics_repository,
    )

    ticket_dispatched_handler = providers.Factory(
        TicketDispatchedHandler,
        ticket_activity_repository=ticket_activity_repository,
        ticket_analytics_repository=ticket_analytics_repository,
        id_generator=id_generator,
    )

    ticket_acknowledged_handler = providers.Factory(
        TicketAcknowledgedHandler,
        ticket_activity_repository=ticket_activity_repository,
        ticket_analytics_repository=ticket_analytics_repository,
        performance_metric_repository=performance_metric_repository,
        agent_score_repository=agent_score_repository,
        id_generator=id_generator,
    )

    ticket_forwarded_handler = providers.Factory(
        TicketForwardedHandler,
        ticket_activity_repository=ticket_activity_repository,
        ticket_analytics_repository=ticket_analytics_repository,
        performance_metric_repository=performance_metric_repository,
        agent_score_repository=agent_score_repository,
        id_generator=id_generator,
    )

    ticket_escalated_handler = providers.Factory(
        TicketEscalatedHandler,
        ticket_activity_repository=ticket_activity_repository,
        ticket_analytics_repository=ticket_analytics_repository,
        performance_metric_repository=performance_metric_repository,
        agent_score_repository=agent_score_repository,
        id_generator=id_generator,
    )

    ticket_completed_handler = providers.Factory(
        TicketCompletedHandler,
        ticket_activity_repository=ticket_activity_repository,
        ticket_analytics_repository=ticket_analytics_repository,
        performance_metric_repository=performance_metric_repository,
        agent_score_repository=agent_score_repository,
        id_generator=id_generator,
    )

    sla_breached_handler = providers.Factory(
        SLABreachedHandler,
        ticket_activity_repository=ticket_activity_repository,
        performance_metric_repository=performance_metric_repository,
        agent_score_repository=agent_score_repository,
        id_generator=id_generator,
    )

    event_handlers = providers.List(
        ticket_created_handler,
        ticket_dispatched_handler,
        ticket_acknowledged_handler,
        ticket_forwarded_handler,
        ticket_escalated_handler,
        ticket_completed_handler,
        sla_breached_handler,
    )

    analytics_event_service = providers.Factory(
        AnalyticsEventService,
        analytics_event_repository=analytics_event_repository,
        id_generator=id_generator,
        datetime_provider=datetime_provider,
        unit_of_work=unit_of_work
    )

    event_dispatcher = providers.Factory(EventDispatcher, handlers=event_handlers)

    event_ingestion = providers.Factory(
        EventIngestion,
        analytics_event_service=analytics_event_service,
    )

    event_processor = providers.Factory(
        EventProcessor,
        analytics_event_service=analytics_event_service,
        event_dispatcher=event_dispatcher,
        unit_of_work=unit_of_work
    )


container = Container()
