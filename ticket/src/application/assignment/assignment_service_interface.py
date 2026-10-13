from abc import ABC, abstractmethod

from application.assignment.dto.assignment_dto import AssignmentResponseDTO, InitialAssignmentCreateDTO, ReassignmentDTO

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
    async def create_initial_assignment(self, payload : InitialAssignmentCreateDTO, current_user_id : str) -> AssignmentResponseDTO : pass

    @abstractmethod
    async def create_reassignment(
        self,
        payload: ReassignmentDTO,
        current_user_id : str
    ) -> AssignmentResponseDTO:
        pass

    @abstractmethod
    async def acknowledge(
        self,
        assignment_id: str,
        agent_id: str,
    ) -> AssignmentResponseDTO:
        pass

    @abstractmethod
    async def claim(
        self,
        assignment_id: str,
        agent_id: str,
    ) -> AssignmentResponseDTO:
        pass

    @abstractmethod
    async def start(
        self,
        assignment_id: str,
        agent_id: str,
    ) -> AssignmentResponseDTO:
        pass

    @abstractmethod
    async def complete(
        self,
        assignment_id: str,
        agent_id: str,
    ) -> AssignmentResponseDTO:
        pass
