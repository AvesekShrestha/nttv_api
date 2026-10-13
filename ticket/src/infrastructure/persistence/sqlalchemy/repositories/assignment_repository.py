from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.assignment.assignment_aggregate import AssignmentAggregate

from infrastructure.persistence.sqlalchemy.mappers.assignement_mappper import AssignmentMapper
from src.application.interfaces.assignment_repository_interface import IAssignmentRepository

from src.infrastructure.persistence.sqlalchemy.models.assignment_model import Assignment


class AssignmentRepository(IAssignmentRepository) : 

    def __init__(self, session : AsyncSession) : 
        self.session = session

    async def get_by_id(self, assignment_id: str) -> AssignmentAggregate | None:

        statement = select(Assignment).where(Assignment.id == assignment_id)
        result = await self.session.execute(statement=statement)

        assignement = result.scalar_one_or_none()

        if assignement is None : return None

        return AssignmentMapper.to_domain(assignement)

    async def add(self, assignment: AssignmentAggregate) -> AssignmentAggregate:

        assignment_model = AssignmentMapper.to_model(assignment)

        self.session.add(assignment_model)
        await self.session.flush()

        return AssignmentMapper.to_domain(assignment_model)

    async def update(self, assignment: AssignmentAggregate) -> AssignmentAggregate:

        assignment_model = AssignmentMapper.to_model(assignment)

        await self.session.merge(assignment_model)
        await self.session.flush()
