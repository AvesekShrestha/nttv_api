from sqlalchemy import event
from sqlalchemy.sql.functions import user

from ticket.application.events.kafka_event import KafkaEvent
from ticket.application.events.ticket_acknowledge_event import TicketAcknowledgeEvent
from ticket.application.events.ticket_completed_event import TicketCompletedEvent
from ticket.application.ticket.dto.activity_response_dto import TicketActivityResponseDTO
from ticket.domain.assignment.exceptions.assignment_exception import AssignmentNotFound
from ticket.domain.outbox.entity.outbox_event_entity import OutboxEvent
from ticket.domain.ticket.entity.ticket_activity_entity import TicketActivityEntity
from ticket.domain.ticket.ticket_activity_type import TicketActivityType
from ticket.domain.ticket.ticket_aggregate import TicketAggregrate
from ticket.domain.ticket.ticket_priority import TicketPriority
from ticket.domain.ticket.ticket_status import TicketStatus


from ticket.application.ticket.dto.ticket_create_dto import TicketCreateDTO
from ticket.application.ticket.dto.ticket_response_dto import TicketResponseDTO
from ticket.application.shared.id_generator_interface import IIdGenerator
from ticket.application.interfaces.ticket_repository_interface import ITicketRepository
from ticket.application.shared.date_time_provider_interface import IDateTimeProvider
from ticket.application.events.ticket_created_event import TicketCreatedEvent
from ticket.application.exceptions.ticket_exception import TicketNotFound
from ticket.application.ticket.ticket_service_interface import ITicketService
from ticket.application.interfaces.outbox_repository_interface import IOutboxRepository
from ticket.application.interfaces.assignment_repository_interface import IAssignmentRepository


from ticket.infrastructure.persistence.sqlalchemy.models import activities_model
from ticket.infrastructure.persistence.sqlalchemy.models.activities_model import TicketActivity
from ticket.infrastructure.persistence.sqlalchemy.unit_of_work import IUnitOfWork



class TicketService(ITicketService) : 

    def __init__(
        self,
        id_generator : IIdGenerator,
        ticket_repository : ITicketRepository,
        outbox_repository : IOutboxRepository,
        assignment_repository : IAssignmentRepository,
        datetime_provider : IDateTimeProvider,
        unit_of_work : IUnitOfWork

    ) : 
        self.id_generator = id_generator
        self.ticket_repository = ticket_repository
        self.outbox_repository = outbox_repository
        self.assignment_repository = assignment_repository
        self.datetime_provider = datetime_provider
        self.unit_of_work = unit_of_work

    async def get_by_id(self, ticket_id: str) -> TicketResponseDTO:

        ticket = await self.ticket_repository.get_by_id(ticket_id=ticket_id)
        
        if ticket is None: 
            raise TicketNotFound(f"Ticket with id:{ticket_id} not found")

        return self._to_response(ticket)

    async def get_all(self, page:int | None = 1, limit:int | None = 5) -> list[TicketResponseDTO]:

        if page is None : page = 1
        if limit is None : limit = 5

        tickets = await self.ticket_repository.get_all(limit=limit, page=page)

        return [
            self._to_response(ticket)
            for ticket in tickets
        ]

    async def create(self, payload : TicketCreateDTO, user_id : str) -> TicketResponseDTO:

        ticket_id = self.id_generator.generate_ticket_id()
        ticket = TicketAggregrate.create(
            id=ticket_id,
            title=payload.title,
            description=payload.description,
            category_id=payload.category_id,
            created_by=user_id
        )

        ticket_activity_id = self.id_generator.generate_ticket_activities_id()
        ticket.record_activity(
            activity_id=ticket_activity_id,
            activity_type=TicketActivityType.CREATED,
            actor_id=user_id
        )

        await self.ticket_repository.add(ticket)

        event_data : TicketCreatedEvent = TicketCreatedEvent(
            ticket_id=ticket_id
        )
        event =  OutboxEvent.create(
            key=user_id,
            event_id=self.id_generator.generate_event_id(),
            event_type="ticket.created",
            occurred_at=self.datetime_provider.now(),
            data=event_data.model_dump(mode="json")
        )

        await self.outbox_repository.add(event=event)

        await self.unit_of_work.commit()

        return self._to_response(ticket)

    async def delete(self, ticket_id: str) -> bool:
        await self.ticket_repository.delete(ticket_id=ticket_id)
        return True

    async def acknowldege(self, ticket_id: str, user_id: str) -> TicketResponseDTO:

        now = self.datetime_provider.now()

        ticket = await self.ticket_repository.get_by_id(ticket_id=ticket_id)
        if ticket is None : raise TicketNotFound(f"Ticket with id : {ticket_id} is not found")

        assignment = await self.assignment_repository.get_by_id(assignment_id=ticket.get_current_assignment_id())
        if assignment is None : raise AssignmentNotFound(f"Assignment not founnd")

        assignment.acknowledge(
            agent_id=user_id,
            at=now
        )

        ticket.acknowldege()

        activity_id : str = self.id_generator.generate_ticket_activities_id()
        activtity = TicketActivityEntity.create(
            id=activity_id,
            ticket_id=ticket_id,
            activity_type=TicketActivityType.ACKNOWLEDGE,
            actor_id=user_id,
            created_at=now
        )

        ticket.record_activity(
            activity_id=activity_id,
            activity_type=TicketActivityType.ACKNOWLEDGE,
            actor_id=user_id
        )

        await self.ticket_repository.update(ticket)

        event_data : TicketAcknowledgeEvent = TicketAcknowledgeEvent(
            ticket_id=ticket_id,
            user_id=user_id
        )

        event_id = self.id_generator.generate_event_id()
        event = OutboxEvent.create(
            key=user_id,
            event_id=event_id,
            event_type="ticket.acknowledge",
            occurred_at=now,
            data=event_data.model_dump(mode="json")
        )

        await self.outbox_repository.add(event=event)

        await self.unit_of_work.commit()
        return self._to_response(aggregate=ticket)

    async def complete(self, ticket_id: str, user_id: str) -> TicketResponseDTO:

        now = self.datetime_provider.now()

        ticket = await self.ticket_repository.get_by_id(ticket_id=ticket_id)
        if ticket is None : raise TicketNotFound(f"Ticket with id : {ticket_id} is not found")

        assignment = await self.assignment_repository.get_by_id(assignment_id=ticket.get_current_assignment_id())
        if assignment is None : raise AssignmentNotFound(f"Assignment not founnd")

        assignment.mark_completed(at=now)

        ticket.complete(at=now)

        activity_id : str = self.id_generator.generate_ticket_activities_id()
        activtity = TicketActivityEntity.create(
            id=activity_id,
            ticket_id=ticket_id,
            activity_type=TicketActivityType.COMPLETED,
            actor_id=user_id,
            created_at=now
        )

        ticket.record_activity(
            activity_id=activity_id,
            activity_type=TicketActivityType.COMPLETED,
            actor_id=user_id
        )

        await self.ticket_repository.update(ticket)

        event_data : TicketCompletedEvent = TicketCompletedEvent(
            ticket_id=ticket_id,
            user_id=user_id
        )

        event_id = self.id_generator.generate_event_id()
        event = OutboxEvent.create(
            key=user_id,
            event_id=event_id,
            event_type="ticket.completed",
            occurred_at=now,
            data=event_data.model_dump(mode="json")
        )

        await self.outbox_repository.add(event=event)

        await self.unit_of_work.commit()
        return self._to_response(aggregate=ticket)




    def _to_response(
        self,
        aggregate: TicketAggregrate,
    ) -> TicketResponseDTO:

        return TicketResponseDTO(
            id=aggregate.id,
            title=aggregate.title,
            description=aggregate.description,
            priority=aggregate.priority.value,
            status=aggregate.status.value,
            category_id=aggregate.category_id,
            created_by=aggregate.created_by,
            current_assignment_id=aggregate.current_assignment_id,

            activities=[
                TicketActivityResponseDTO(
                    id=activity.id,
                    ticket_id=activity.ticket_id,
                    activity_type=activity.activity_type,
                    actor_id=activity.actor_id,
                    created_at=activity.created_at,
                )
                for activity in aggregate.activities
            ],

            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
            resolved_at=aggregate.resolved_at,
        )
