from ticket.application.exceptions.ticket_exception import TicketNotFound
from ticket.application.ticket.ticket_service_interface import ITicketService
from ticket.domain.ticket.entity.ticket_activity_entity import TicketActivityEntity
from ticket.domain.ticket.ticket_activity_type import TicketActivityType
from ticket.domain.ticket.ticket_aggregate import TicketAggregrate

from ticket.application.ticket.dto.ticket_create_dto import TicketCreateDTO
from ticket.application.ticket.dto.ticket_response_dto import TicketResponseDTO
from ticket.application.shared.id_generator_interface import IIdGenerator
from ticket.application.interfaces.ticket_repository_interface import ITicketRepository
from ticket.application.interfaces.activity_repository_interface import IActivityRepository

from ticket.domain.ticket.ticket_priority import TicketPriority
from ticket.domain.ticket.ticket_status import TicketStatus
from ticket.infrastructure.persistence.sqlalchemy.models.activities_model import TicketActivity
from ticket.infrastructure.persistence.sqlalchemy.unit_of_work import IUnitOfWork



class TicketService(ITicketService) : 

    def __init__(
        self,
        id_generator : IIdGenerator,
        ticket_repository : ITicketRepository,
        ticket_activity_repository : IActivityRepository,
        unit_of_work : IUnitOfWork

    ) : 
        self.id_generator = id_generator
        self.ticket_repository = ticket_repository
        self.ticket_activity_repository = ticket_activity_repository
        self.unit_of_work = unit_of_work

    async def get_by_id(self, ticket_id: str) -> TicketResponseDTO:

        ticket = await self.ticket_repository.get_by_id(ticket_id=ticket_id)
        
        if ticket is None: 
            raise TicketNotFound(f"Ticket with id:{ticket_id} not found")

        return self._to_response(ticket)

    async def get_all(self, page:int, limit:int) -> list[TicketResponseDTO]:

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
        activity = TicketActivityEntity.create(
            id=ticket_activity_id,
            ticket_id=ticket_id,
            activity_type=TicketActivityType.CREATED,
            actor_id=user_id
        )

        await self.ticket_repository.add(ticket)
        await self.ticket_activity_repository.add(activity)

        await self.unit_of_work.commit()

        return self._to_response(ticket)

    async def delete(self, ticket_id: str) -> bool:
        await self.ticket_repository.delete(ticket_id=ticket_id)
        return True



    def _to_response(self, aggregate : TicketAggregrate) -> TicketResponseDTO : 

        return TicketResponseDTO(
            id=aggregate.id,
            title=aggregate.title,
            description=aggregate.description,
            priority=TicketPriority.from_string(aggregate.priority),
            status=TicketStatus.from_string(aggregate.status),
            category_id=aggregate.category_id,
            created_by=aggregate.created_by,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
            resolved_at=aggregate.resolved_at
        )
