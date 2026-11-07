from datetime import date

import httpx

from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector import containers, providers

from ticket.application.ticket.ticket_service import TicketService
from ticket.application.assignment.assignment_service import AssignmentService

from ticket.config import settings

from ticket.infrastructure.messaging.consumer import Dispatcher
from ticket.infrastructure.persistence.sqlalchemy.unit_of_work import UnitOfWork
from ticket.infrastructure.persistence.sqlalchemy.repositories.ticket_repository import TicketRepository
from ticket.infrastructure.persistence.sqlalchemy.repositories.assignment_repository import AssignmentRepository
from ticket.infrastructure.persistence.sqlalchemy.repositories.outbox_repository import OutboxRepository
from ticket.infrastructure.persistence.sqlalchemy.repositories.processed_event_repository import ProcessedEventRepository
from ticket.infrastructure.persistence.sqlalchemy.repositories.round_robin_repository import RoundRobinRepository
from ticket.infrastructure.identity.date_time_provider import DateTimeProvider
from ticket.infrastructure.identity.id_generator import IIdGenerator, IdGenerator
from ticket.infrastructure.identity.jwt_generator import JWTGenerator
from ticket.infrastructure.messaging.producer import KafkaProducer
from ticket.infrastructure.workers.outbox_worker import OutboxWorker


from ticket.infrastructure.clients.origanization_client import OrganizationClient
from ticket.infrastructure.workers.sla_worker import SLABreachWorker

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    session = providers.Dependency(instance_of=AsyncSession)

    http_client = providers.Singleton(
        httpx.AsyncClient,
        base_url=settings.ORGANIZATION_SERVICE_URL,
        timeout=5.0
    )

    organization_client = providers.Singleton(
        OrganizationClient,
        http_client=http_client
    )

    id_generator = providers.Singleton(IdGenerator)
    datetime_provider = providers.Singleton(DateTimeProvider)
    producer = providers.Singleton(KafkaProducer)
    jwt_generator = providers.Singleton(JWTGenerator)


    unit_of_work = providers.Factory(
        UnitOfWork,
        session=session
    )

    ticket_repository = providers.Factory(
        TicketRepository,
        session=session,
        datetime_provider=datetime_provider

    )

    assignment_repository = providers.Factory(
        AssignmentRepository,
        session=session,
        datetime_provider=datetime_provider
    )
    processed_event_repository = providers.Factory(
        ProcessedEventRepository,
        session=session
    )
    round_robin_repository = providers.Factory(
        RoundRobinRepository,
        session=session
    )
    outbox_repository = providers.Factory(
        OutboxRepository,
        session=session
    )

    ticket_service = providers.Factory(
        TicketService,
        id_generator = id_generator,
        ticket_repository=ticket_repository,
        outbox_repository=outbox_repository,
        assignment_repository=assignment_repository,
        datetime_provider=datetime_provider,
        unit_of_work=unit_of_work
    )


    assignment_service = providers.Factory(
        AssignmentService,
        assignment_repository=assignment_repository,
        ticket_repository=ticket_repository,
        round_robin_repository=round_robin_repository,
        outbox_repository=outbox_repository,
        organization_client=organization_client,
        id_generator=id_generator,
        datetime_provider=datetime_provider,
        unit_of_work=unit_of_work
    )

    dispatcher = providers.Factory(
        Dispatcher,
        processed_event_repository=processed_event_repository,
        assignment_service=assignment_service,
        datetime_provider=datetime_provider
    )

    outbox_worker = providers.Factory(
        OutboxWorker,
        producer=producer,
        outbox_repository=outbox_repository,
        datetime_provider=datetime_provider,
        unit_of_work=unit_of_work
    )

    sla_worker = providers.Factory(
        SLABreachWorker,
        assignment_repository=assignment_repository,
        outbox_repository=outbox_repository,
        id_generator=id_generator,
        datetime_provider=datetime_provider,
        unit_of_work=unit_of_work
    )

container = Container()
