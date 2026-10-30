from abc import ABC, abstractmethod

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
    async def get_all(self, page: int, limit : int) -> list[TicketResponseDTO] : pass

    @abstractmethod
    async def create(self, payload : TicketCreateDTO, user_id : str) -> TicketResponseDTO: pass

    @abstractmethod
    async def delete(self, ticket_id : str) -> bool : pass
