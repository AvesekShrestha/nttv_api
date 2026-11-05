from abc import ABC, abstractmethod

from ticket.domain.ticket.ticket_aggregate import TicketAggregrate


class ITicketRepository(ABC):

    @abstractmethod
    async def get_by_id(
        self,
        ticket_id: str,
    ) -> TicketAggregrate | None:
        raise NotImplementedError

    @abstractmethod
    async def get_all(
        self,
        limit: int = 5,
        page: int = 1,
    ) -> list[TicketAggregrate]:
        raise NotImplementedError

    @abstractmethod
    async def add(
        self,
        aggregate: TicketAggregrate,
    ) -> TicketAggregrate:
        raise NotImplementedError

    @abstractmethod
    async def update(
        self,
        aggregate: TicketAggregrate,
    ) -> TicketAggregrate:
        raise NotImplementedError

    @abstractmethod
    async def delete(
        self,
        ticket_id: str,
    ) -> None:
        raise NotImplementedError
