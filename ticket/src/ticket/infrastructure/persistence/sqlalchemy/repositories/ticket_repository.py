import re

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ticket.application.interfaces.ticket_repository_interface import ITicketRepository

from ticket.domain.ticket.ticket_aggregate import TicketAggregrate

from ticket.infrastructure.persistence.sqlalchemy.mappers.ticket_mapper import TicketMapper
from ticket.infrastructure.persistence.sqlalchemy.models.ticket_model import Ticket


class TicketRepository(ITicketRepository) : 
    def __init__(self, session : AsyncSession): 
        self.session = session

    async def get_by_id(self, ticket_id: str) -> TicketAggregrate | None:

        stmt = select(Ticket).where(Ticket.id == ticket_id)
        result = await self.session.execute(stmt)

        ticket = result.scalar_one_or_none()

        if ticket is None:
            return None

        return TicketMapper.to_domain(ticket)

    async def get_all(self, limit: int = 5, page : int = 1) -> list[TicketAggregrate]:

        offset = (page -1) * limit

        stmt = select(Ticket).offset(offset=offset).limit(limit=limit).order_by(Ticket.created_at.desc())
        result = await self.session.execute(stmt)

        tickets = result.scalars().all()

        return [
            TicketMapper.to_domain(ticket)
            for ticket in tickets
        ]

    async def add(self, aggregate: TicketAggregrate) -> TicketAggregrate:

        ticket = TicketMapper.to_model(aggregate=aggregate)

        self.session.add(ticket)
        await self.session.flush()

        return TicketMapper.to_domain(ticket)

    async def update(self, aggregate: TicketAggregrate) -> TicketAggregrate:

        ticket = TicketMapper.to_model(aggregate=aggregate)

        await self.session.merge(ticket)
        await self.session.flush()

        return TicketMapper.to_domain(ticket)

    async def delete(self, ticket_id: str) -> None:
        statement = delete(Ticket).where(Ticket.id == ticket_id)
        await self.session.execute(statement=statement)
        await self.session.flush()

        return None
