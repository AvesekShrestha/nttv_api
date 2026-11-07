from abc import ABC, abstractmethod

from ticket.application.assignment.dto.assignment_dto import AssignmentResponseDTO, ReassignmentDTO
from ticket.application.assignment.dto.assignment_query_dto import AssignmentQueryDTO
from ticket.application.assignment.dto.claim_eligibility_dto import ClaimEligibilityResponse
from ticket.application.shared.pagination_response_dto import PaginatedResponse
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
    async def get_all(self, query : AssignmentQueryDTO) -> PaginatedResponse[AssignmentResponseDTO] : pass

    @abstractmethod
    async def dispatch(self, ticket_id : str) -> AssignmentResponseDTO :
        pass

    @abstractmethod
    async def forward(self, ticket_id : str, actor_id: str, payload : ReassignmentDTO) -> AssignmentResponseDTO : pass

    @abstractmethod
    async def escalate(self, ticket_id : str, actor_id: str, payload : ReassignmentDTO) -> AssignmentResponseDTO : pass

    @abstractmethod
    async def claim_eligibility(self, assignment_id : str, agent_id : str) -> ClaimEligibilityResponse : pass
