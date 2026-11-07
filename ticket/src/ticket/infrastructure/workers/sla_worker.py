import asyncio
from datetime import datetime
import logging

from ticket.application.assignment.assignment_service_interface import IAssignmentService
from ticket.application.assignment.dto.assignment_query_dto import AssignmentQueryDTO
from ticket.application.events.sla_brached_event import SLABreachedEvent
from ticket.application.interfaces.assignment_repository_interface import IAssignmentRepository
from ticket.application.interfaces.outbox_repository_interface import IOutboxRepository
from ticket.application.shared.application_exception import ApplicationException
from ticket.application.shared.date_time_provider_interface import IDateTimeProvider
from ticket.application.shared.id_generator_interface import IIdGenerator
from ticket.application.shared.pagination_response_dto import PaginatedResponse
from ticket.application.shared.unit_of_work_interface import IUnitOfWork
from ticket.domain.assignment.assignment_aggregate import AssignmentAggregate
from ticket.domain.outbox.entity.outbox_event_entity import OutboxEvent
from ticket.domain.shared.domain_exception import DomainException

logger = logging.getLogger(__name__)

class SLABreachWorker:

    def __init__(
        self,
        assignment_repository : IAssignmentRepository,
        outbox_repository : IOutboxRepository,
        id_generator : IIdGenerator,
        datetime_provider : IDateTimeProvider,
        unit_of_work : IUnitOfWork,
        interval: int = 30,
    ):
        self.assignment_repository = assignment_repository
        self.outbox_repository = outbox_repository
        self.id_generator = id_generator
        self.datetime_provider = datetime_provider
        self.unit_of_work = unit_of_work
        self.interval = interval

    async def run(self):

        now = self.datetime_provider.now()

        logger.info("SLA breach worker started")

        while True:
            try:
                await self.process_acknowledgment_breaches(now=now)
                await self.process_resolution_breaches(now=now)

            except (ApplicationException, DomainException) as e:
                print(f"Status : {e.status} and message : {e.message}")

            except asyncio.CancelledError:
                logger.info("SLA breach worker stopped")
                raise

            except Exception:
                logger.exception("Error while processing SLA breaches")

            await asyncio.sleep(self.interval)

    async def process_acknowledgment_breaches(self, now : datetime):

        query = AssignmentQueryDTO(
            acknowledgment_sla_breached=True,
            acknowledgment_sla_breached_recorded=False,
            status="PENDING"
        )

        assignments : PaginatedResponse[AssignmentAggregate] = await self.assignment_repository.get_all(query=query)

        logger.info(
            "Found %s acknowledgment SLA breached assignments",
            assignments.total,
        )

        for assignment in assignments.items:
            try:
                assignment.mark_acknowledgment_sla_breached(now)

                event_data : SLABreachedEvent = SLABreachedEvent(
                    assignment_id=assignment.id,
                    ticket_id=assignment.ticket_id
                )

                event_id : str = self.id_generator.generate_event_id()
                event = OutboxEvent.create(
                    key=assignment.ticket_id,
                    event_id=event_id,
                    event_type="ticket.breached",
                    occurred_at=now,
                    data=event_data.model_dump(mode="json")
                )

                await self.assignment_repository.update(aggregate=assignment)
                await self.outbox_repository.add(event=event)

                await self.unit_of_work.commit()

            except (ApplicationException, DomainException) as e:
                print(f"Status :{e.status} and message : {e.message}")

            except Exception:
                logger.exception(
                    "Failed to handle acknowledgment SLA breach: %s",
                    assignment.id,
                )

    async def process_resolution_breaches(self, now:datetime):
        query = AssignmentQueryDTO(
            resolution_sla_breached=True,
            resolution_sla_breached_recorded=False,
        )

        assignments : PaginatedResponse[AssignmentAggregate] = await self.assignment_repository.get_all(query=query)

        logger.info(
            "Found %s resolution SLA breached assignments",
            assignments.total,
        )

        for assignment in assignments.items:
            try:
                assignment.mark_resolution_sla_breached(now)

                event_data : SLABreachedEvent = SLABreachedEvent(
                    assignment_id=assignment.id,
                    ticket_id=assignment.ticket_id
                )

                event_id : str = self.id_generator.generate_event_id()
                event = OutboxEvent.create(
                    key=assignment.ticket_id,
                    event_id=event_id,
                    event_type="ticket.breached",
                    occurred_at=now,
                    data=event_data.model_dump(mode="json")
                )

                await self.assignment_repository.update(aggregate=assignment)
                await self.outbox_repository.add(event=event)

                await self.unit_of_work.commit()

            except (ApplicationException, DomainException) as e:
                print(f"Status :{e.status} and message : {e.message}")

            except Exception:
                logger.exception(
                    "Failed to handle acknowledgment SLA breach: %s",
                    assignment.id,
                )
