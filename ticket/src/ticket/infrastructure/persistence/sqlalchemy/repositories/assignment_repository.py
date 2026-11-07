from sqlalchemy import delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ticket.application.assignment.dto.assignment_query_dto import AssignmentQueryDTO
from ticket.application.interfaces.assignment_repository_interface import (
    IAssignmentRepository,
)
from ticket.application.shared.pagination_response_dto import PaginatedResponse
from ticket.application.shared.date_time_provider_interface import IDateTimeProvider
from ticket.domain.assignment.assignment_aggregate import AssignmentAggregate



from ticket.infrastructure.persistence.sqlalchemy.mappers.assignement_mappper import AssignmentMapper
from ticket.infrastructure.persistence.sqlalchemy.models import assignment_model
from ticket.infrastructure.persistence.sqlalchemy.models.assignment_model import (
    Assignment,
)
from ticket.infrastructure.persistence.sqlalchemy.models.assignment_team_recipient_model import AssignmentTeamRecipient


class AssignmentRepository(IAssignmentRepository):

    def __init__(self, session: AsyncSession, datetime_provider : IDateTimeProvider):
        self.session = session
        self.datetime_provider = datetime_provider

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


    async def get_all(self, query: AssignmentQueryDTO) -> PaginatedResponse[AssignmentAggregate]:

        now = self.datetime_provider.now()

        filters = []

        if query.ticket_id is not None:
            filters.append(
                Assignment.ticket_id == query.ticket_id
            )

        if query.status is not None:
            filters.append(
                Assignment.status == query.status
            )

        if query.acknowledgment_sla_breached is not None:
            if query.acknowledgment_sla_breached:
                filters.append(
                    Assignment.acknowledgment_deadline_at < now
                )
            else:
                filters.append(
                    Assignment.acknowledgment_deadline_at >= now
                )

        if query.resolution_sla_breached is not None:
            if query.resolution_sla_breached:
                filters.append(
                    Assignment.resolution_deadline_at < now
                )
            else:
                filters.append(
                    Assignment.resolution_deadline_at >= now
                )

        if query.acknowledgment_sla_breached_recorded is not None:
            if query.acknowledgment_sla_breached_recorded:
                filters.append(
                    Assignment.acknowledgment_sla_breached_at.is_not(None)
                )
            else:
                filters.append(
                    Assignment.acknowledgment_sla_breached_at.is_(None)
                )

        if query.resolution_sla_breached_recorded is not None:
            if query.resolution_sla_breached_recorded:
                filters.append(
                    Assignment.resolution_sla_breached_at.is_not(None)
                )
            else:
                filters.append(
                    Assignment.resolution_sla_breached_at.is_(None)
                )

        sort_column = getattr(Assignment, query.sort_by)

        if query.sort_order == "desc":
            sort_column = sort_column.desc()
        else:
            sort_column = sort_column.asc()

        count_stmt = (
            select(func.count(Assignment.id))
            .where(*filters)
        )

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = (
            select(Assignment)
            .options(
                selectinload(Assignment.team_recipients)
                .selectinload(
                    AssignmentTeamRecipient.agent_recipients
                )
            )
            .where(*filters)
            .order_by(sort_column)
            .offset(query.offset)
            .limit(query.limit)
        )
        result = await self.session.execute(stmt)

        assignments = result.scalars().all()

        return PaginatedResponse(
            items=[
                AssignmentMapper.to_domain(model=assignment)
                for assignment in assignments
            ],
            total=total or 0,
            page=query.page,
            limit=query.limit,
        )

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
