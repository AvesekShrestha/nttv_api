from abc import ABC, abstractmethod

from ticket.application.assignment.dto.assignment_dto import AssignmentResponseDTO, ReassignmentDTO
from ticket.domain.rotation.round_robin_scope import RoundRobinScope

class IAssignmentService(ABC):

    @abstractmethod
    async def get_by_id(self, assignment_id : str) -> AssignmentResponseDTO : pass

    @abstractmethod
    async def get_by_ticket_id(
        self,
        ticket_id: str,
    ) -> list[AssignmentResponseDTO]: 
        pass

    @abstractmethod
    async def dispatch(self, ticket_id : str) -> AssignmentResponseDTO :
        pass

    @abstractmethod
    async def forward(self, ticket_id : str, actor_id: str, payload : ReassignmentDTO) -> AssignmentResponseDTO : pass

    @abstractmethod
    async def escalate(self, ticket_id : str, actor_id: str, payload : ReassignmentDTO) -> AssignmentResponseDTO : pass
