from abc import ABC, abstractmethod
from typing import Optional

from analytics.domain.ticket_activity.entity.ticket_activity_entity import (
    TicketActivityEntity,
)


class ITicketActivityRepository(ABC):

    @abstractmethod
    async def save(
        self,
        activity: TicketActivityEntity,
    ) -> None:
        pass

    @abstractmethod
    async def get_by_source_event_id(
        self,
        source_event_id: str,
    ) -> Optional[TicketActivityEntity]:
        pass

    @abstractmethod
    async def get_by_ticket_id(
        self,
        ticket_id: str,
    ) -> list[TicketActivityEntity]:
        pass
