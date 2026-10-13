from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.assignment.assignment_aggregate import AssignmentAggregate


class IAssignmentRepository(ABC):

    @abstractmethod
    async def get_by_id(
        self,
        assignment_id: str,
    ) -> AssignmentAggregate | None: pass

    @abstractmethod
    async def add(
        self,
        assignment: AssignmentAggregate,
    ) -> AssignmentAggregate:
        pass

    @abstractmethod
    async def update(
        self,
        assignment: AssignmentAggregate,
    ) -> AssignmentAggregate:
        pass


