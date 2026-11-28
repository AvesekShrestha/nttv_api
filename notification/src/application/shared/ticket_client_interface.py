from abc import ABC, abstractmethod

from src.application.dto.ticket_data_dto import (
    AssignmentDetails,
    TicketDetails,
)


class TicketClientInterface(ABC):
    @abstractmethod
    async def get_ticket(self, ticket_id: str) -> TicketDetails:
        raise NotImplementedError

    @abstractmethod
    async def get_assignment(
        self,
        assignment_id: str,
    ) -> AssignmentDetails:
        raise NotImplementedError
