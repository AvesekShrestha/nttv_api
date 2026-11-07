from sqlalchemy import delete, func, select, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ticket.application.interfaces.ticket_repository_interface import (
    ITicketRepository,
)
from ticket.application.shared.date_time_provider_interface import IDateTimeProvider
from ticket.application.shared.pagination_response_dto import PaginatedResponse
from ticket.application.ticket.dto import ticket_create_dto
from ticket.application.ticket.dto.ticket_query_dto import TicketQueryDTO
from ticket.domain.ticket.ticket_aggregate import TicketAggregrate
from ticket.infrastructure.persistence.sqlalchemy.mappers.ticket_mapper import (
    TicketMapper,
)
from ticket.infrastructure.persistence.sqlalchemy.models.assignment_agent_recipient_model import AssignmentAgentRecipient
from ticket.infrastructure.persistence.sqlalchemy.models.assignment_model import Assignment
from ticket.infrastructure.persistence.sqlalchemy.models.assignment_team_recipient_model import AssignmentTeamRecipient
from ticket.infrastructure.persistence.sqlalchemy.models.ticket_model import (
    Ticket,
)


class TicketRepository(ITicketRepository):

    def __init__(self, session: AsyncSession, datetime_provider : IDateTimeProvider):
        self.session = session
        self.datetime_provider=datetime_provider


    async def get_by_id(
        self,
        ticket_id: str,
    ) -> TicketAggregrate | None:

        stmt = (
            select(Ticket)
            .options(selectinload(Ticket.activities))
            .where(Ticket.id == ticket_id)
        )

        result = await self.session.execute(stmt)
        ticket = result.scalar_one_or_none()

        if ticket is None:
            return None

        return TicketMapper.to_domain(ticket)


    async def get_all(
        self,
        query: TicketQueryDTO,
    ) -> PaginatedResponse[TicketAggregrate]:
        now = self.datetime_provider.now()

        filters = []

        if query.user_id is not None:

            responsible_condition = (
                Assignment.responsible_agent_id == query.user_id
            )

            recipient_exists = (
                select(AssignmentAgentRecipient.id)
                .join(
                    AssignmentTeamRecipient,
                    AssignmentTeamRecipient.id
                    == AssignmentAgentRecipient.team_recipient_id,
                )
                .where(
                    AssignmentTeamRecipient.assignment_id == Assignment.id,
                    AssignmentAgentRecipient.agent_id == query.user_id,
                )
                .exists()
            )

            backup_condition = and_(
                Assignment.responsible_agent_id.is_distinct_from(
                    query.user_id
                ),
                recipient_exists,
            )

            if query.assignment_role == "responsible":
                filters.append(responsible_condition)

            elif query.assignment_role == "backup":
                filters.append(backup_condition)

            else:
                filters.append(
                    or_(
                        responsible_condition,
                        backup_condition,
                    )
                )

        if query.ticket_id is not None:
            filters.append(Ticket.id == query.ticket_id)

        if query.category_id is not None:
            filters.append(Ticket.category_id == query.category_id)

        if query.created_by is not None:
            filters.append(Ticket.created_by == query.created_by)

        if query.status is not None:
            filters.append(Ticket.status == query.status.value)

        if query.priority is not None:
            filters.append(Ticket.priority == query.priority.value)


        if query.search is not None:
            search_term = f"%{query.search.strip()}%"

            filters.append(
                or_(
                    Ticket.id.ilike(search_term),
                    Ticket.title.ilike(search_term),
                )
            )

        if query.acknowledgment_sla_breached is not None:

            acknowledgment_breached = and_(
                Assignment.acknowledged_at.is_(None),
                Assignment.acknowledgment_deadline_at < now,
            )

            if query.acknowledgment_sla_breached:
                filters.append(acknowledgment_breached)
            else:
                filters.append(
                    or_(
                        Assignment.acknowledged_at.is_not(None),
                        Assignment.acknowledgment_deadline_at >= now,
                    )
                )

        if query.resolution_sla_breached is not None:

            resolution_breached = and_(
                Assignment.completed_at.is_(None),
                Assignment.resolution_deadline_at < now,
            )

            if query.resolution_sla_breached:
                filters.append(resolution_breached)
            else:
                filters.append(
                    or_(
                        Assignment.completed_at.is_not(None),
                        Assignment.resolution_deadline_at >= now,
                    )
                )

        base_stmt = (
            select(Ticket)
            .outerjoin(
                Assignment,
                Assignment.id == Ticket.current_assignment_id,
            )
            .where(*filters)
        )


        count_stmt = (
            select(func.count())
            .select_from(
                base_stmt.order_by(None).subquery()
            )
        )

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()


        sort_columns = {
            "created_at": Ticket.created_at,
            "updated_at": Ticket.updated_at,
            "status": Ticket.status,
            "priority": case(
                (Ticket.priority == "URGENT", 4),
                (Ticket.priority == "HIGH", 3),
                (Ticket.priority == "MEDIUM", 2),
                (Ticket.priority == "LOW", 1),
                else_=0,
            ),
        }

        sort_column = sort_columns[query.sort_by]

        if query.sort_order == "desc":
            sort_column = sort_column.desc()
        else:
            sort_column = sort_column.asc()

        stmt = (
            base_stmt
            .order_by(
                sort_column,
                Ticket.id.desc(),
            )
            .offset(query.offset)
            .limit(query.limit)
        )

        result = await self.session.execute(stmt)
        tickets = result.scalars().all()

        return PaginatedResponse(
            items=[
                TicketMapper.to_domain_without_activities(model=ticket)
                for ticket in tickets
            ],
            total=total,
            page=query.page,
            limit=query.limit,
        )

    async def add(
        self,
        aggregate: TicketAggregrate,
    ) -> TicketAggregrate:

        ticket_model = TicketMapper.to_model(aggregate)

        self.session.add(ticket_model)
        await self.session.flush()

        return TicketMapper.to_domain(ticket_model)

    async def update(
        self,
        aggregate: TicketAggregrate,
    ) -> TicketAggregrate:

        ticket = TicketMapper.to_model(aggregate=aggregate)

        await self.session.merge(ticket)
        await self.session.flush()

        return TicketMapper.to_domain(ticket)

    async def delete(
        self,
        ticket_id: str,
    ) -> None:

        stmt = delete(Ticket).where(Ticket.id == ticket_id)

        await self.session.execute(stmt)
        await self.session.flush()
