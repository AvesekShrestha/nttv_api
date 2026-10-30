from abc import ABC, abstractmethod

from ticket.domain.ticket.ticket_aggregate import TicketAggregrate

class ITicketRepository(ABC):

    @abstractmethod
    async def get_by_id(
            self,
            ticket_id : str
    ) -> TicketAggregrate | None : pass

    @abstractmethod
    async def get_all(
        self,
        limit : int,
        page : int
    ) -> list[TicketAggregrate] : pass

    @abstractmethod
    async def add(
            self,
            aggregate : TicketAggregrate
    ) -> TicketAggregrate : pass

    @abstractmethod
    async def update(
            self,
            aggregate : TicketAggregrate
    ) -> TicketAggregrate : pass

    @abstractmethod
    async def delete(
            self,
            ticket_id : str 
    )-> None : pass


