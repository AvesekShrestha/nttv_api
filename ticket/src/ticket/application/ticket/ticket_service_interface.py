from abc import ABC, abstractmethod

from ticket.application.shared.pagination_response_dto import PaginatedResponse
from ticket.application.ticket.dto.ticket_query_dto import TicketQueryDTO
from ticket.domain.ticket.ticket_aggregate import TicketAggregrate

from ticket.application.ticket.dto.ticket_create_dto import TicketCreateDTO
from ticket.application.ticket.dto.ticket_response_dto import TicketResponseDTO
from ticket.application.shared.id_generator_interface import IIdGenerator

class ITicketService(ABC) : 

    def __init__(
        self,
        id_generator : IIdGenerator
    ) : 
        self.id_generator = id_generator

    @abstractmethod
    async def get_by_id(self, ticket_id : str) -> TicketResponseDTO : pass

    @abstractmethod
    async def get_all(self, query : TicketQueryDTO) -> PaginatedResponse[TicketResponseDTO] : pass

    @abstractmethod
    async def create(self, payload : TicketCreateDTO, user_id : str) -> TicketResponseDTO: pass

    @abstractmethod
    async def delete(self, ticket_id : str) -> bool : pass

    @abstractmethod
    async def acknowldege(self, ticket_id: str, user_id : str) -> TicketResponseDTO : pass

    @abstractmethod
    async def complete(self, ticket_id: str, user_id : str) -> TicketResponseDTO : pass
