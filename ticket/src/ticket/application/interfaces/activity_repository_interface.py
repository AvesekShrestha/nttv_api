from abc import ABC, abstractmethod
from datetime import datetime

from ticket.domain.ticket.entity.ticket_activity_entity import TicketActivityEntity

class IActivityRepository(ABC):

    @abstractmethod
    async def get_by_id(
        self,
        activity_id: str,
    ) -> TicketActivityEntity | None: pass

    @abstractmethod
    async def get_all(
        self,
        page : int,
        limit : int
    ) -> list[TicketActivityEntity]: pass

    @abstractmethod
    async def add(
        self,
        activity: TicketActivityEntity,
    ) -> TicketActivityEntity:
        pass

    @abstractmethod
    async def delete(
            self,
            activity_id: str
    ) -> None : pass
