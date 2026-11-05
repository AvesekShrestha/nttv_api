from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ticket.application.interfaces.assignment_repository_interface import (
    IAssignmentRepository,
)
from ticket.domain.assignment.assignment_aggregate import AssignmentAggregate



from ticket.infrastructure.persistence.sqlalchemy.mappers.assignement_mappper import AssignmentMapper
from ticket.infrastructure.persistence.sqlalchemy.models import assignment_model
from ticket.infrastructure.persistence.sqlalchemy.models.assignment_model import (
    Assignment,
)
from ticket.infrastructure.persistence.sqlalchemy.models.assignment_team_recipient_model import AssignmentTeamRecipient


class AssignmentRepository(IAssignmentRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        assignment_id: str,
    ) -> AssignmentAggregate | None:

        stmt = (
            select(Assignment)
            .options(
                selectinload(Assignment.team_recipients)
                .selectinload(
                    AssignmentTeamRecipient.agent_recipients
                )
            )
            .where(Assignment.id == assignment_id)
        )

        result = await self.session.execute(stmt)
        assignment = result.scalar_one_or_none()

        if assignment is None:
            return None

        return AssignmentMapper.to_domain(assignment)

    async def get_by_ticket_id(
        self,
        ticket_id: str,
    ) -> list[AssignmentAggregate]:

        stmt = (
            select(Assignment)
            .options(
                selectinload(Assignment.team_recipients)
                .selectinload(
                    AssignmentTeamRecipient.agent_recipients
                )
            )
            .where(Assignment.ticket_id == ticket_id)
            .order_by(Assignment.created_at.desc())
        )

        result = await self.session.execute(stmt)
        assignments = result.scalars().all()

        return [
            AssignmentMapper.to_domain(assignment)
            for assignment in assignments
        ]

    async def add(
        self,
        aggregate: AssignmentAggregate,
    ) -> AssignmentAggregate:

        assignment_model = AssignmentMapper.to_model(aggregate)

        self.session.add(assignment_model)

        await self.session.flush()

        return AssignmentMapper.to_domain(assignment_model)

    async def update(
        self,
        aggregate: AssignmentAggregate,
    ) -> AssignmentAggregate:

        assignment_model = AssignmentMapper.to_model(aggregate=aggregate)
        await self.session.merge(assignment_model)
        await self.session.flush()

        return AssignmentMapper.to_domain(assignment_model)

    async def delete(
        self,
        assignment_id: str,
    ) -> None:

        stmt = delete(Assignment).where(
            Assignment.id == assignment_id
        )
        await self.session.execute(stmt)
        await self.session.flush()
