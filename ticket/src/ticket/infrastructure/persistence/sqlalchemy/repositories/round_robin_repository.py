from sqlalchemy import select
from sqlalchemy.engine import result
from sqlalchemy.ext.asyncio import AsyncSession

from ticket.application.interfaces.round_robin_repository_interface import IRoundRobinRepository
from ticket.domain.rotation.round_robin_aggregate import RoundRobinAggregate
from ticket.infrastructure.persistence.sqlalchemy.mappers.round_robin_mapper import RoundRobinMapper
from ticket.infrastructure.persistence.sqlalchemy.models.round_robin_model import RoundRobinModel


class RoundRobinRepository(IRoundRobinRepository) : 

    def __init__(self, session : AsyncSession) :
        self.session = session

    async def get_by_scope(self, scope_type: str, scope_id : str):
        statement = (
            select(RoundRobinModel)
            .where(
                RoundRobinModel.scope_type == scope_type,
                RoundRobinModel.scope_id == scope_id,
            )
        )

        result = await self.session.execute(statement=statement)
        round_robin = result.scalar_one_or_none()

        if round_robin is None : return None

        return RoundRobinMapper.to_domain(model=round_robin)

    async def add(self, aggregate: RoundRobinAggregate) -> None:
        round_robin_model = RoundRobinMapper.to_model(aggregate=aggregate)

        self.session.add(round_robin_model)
        await self.session.flush()

    async def update(self, aggregate: RoundRobinAggregate) -> None:
        round_robin_model = RoundRobinMapper.to_model(aggregate=aggregate)

        await self.session.merge(round_robin_model)
        await self.session.flush()






        
