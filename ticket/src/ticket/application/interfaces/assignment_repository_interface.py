from abc import ABC, abstractmethod
from datetime import datetime

from ticket.application.assignment.dto.assignment_query_dto import AssignmentQueryDTO
from ticket.application.shared.pagination_response_dto import PaginatedResponse
from ticket.domain.assignment.assignment_aggregate import AssignmentAggregate


class IAssignmentRepository(ABC):

    @abstractmethod
    async def get_by_id(
        self,
        assignment_id: str,
    ) -> AssignmentAggregate | None: pass

    @abstractmethod
    async def get_by_ticket_id(
        self,
        ticket_id: str,
    ) -> list[AssignmentAggregate] : pass

    @abstractmethod
    async def get_all(
        self,
        query : AssignmentQueryDTO
    ) -> PaginatedResponse[AssignmentAggregate] : 
        pass

    @abstractmethod
    async def add(
        self,
        aggregate: AssignmentAggregate,
    ) -> AssignmentAggregate:
        pass

    @abstractmethod
    async def update(
        self,
        aggregate: AssignmentAggregate,
    ) -> AssignmentAggregate:
        pass


