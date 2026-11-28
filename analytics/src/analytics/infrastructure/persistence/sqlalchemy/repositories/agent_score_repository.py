from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from analytics.application.interfaces.agent_score_repository_interface import (
    IAgentScoreRepository,
)

from analytics.domain.agent_score.entity.agent_score_entity import (
    AgentScoreEntity,
)

from analytics.infrastructure.persistence.sqlalchemy.models.agent_score_model import (
    AgentScoreModel,
)

from analytics.infrastructure.persistence.sqlalchemy.mappers.agent_score_mapper import (
    AgentScoreMapper,
)


class AgentScoreRepository(IAgentScoreRepository):

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def save(
        self,
        score: AgentScoreEntity,
    ) -> None:

        model = AgentScoreMapper.to_model(score)

        await self._session.merge(model)
        await self._session.flush()

    async def get_by_source_event_id(
        self,
        source_event_id: str,
    ) -> AgentScoreEntity | None:

        stmt = select(AgentScoreModel).where(
            AgentScoreModel.source_event_id == source_event_id
        )

        result = await self._session.execute(stmt)

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return AgentScoreMapper.to_entity(model)

    async def get_by_agent_id(
        self,
        agent_id: str,
    ) -> list[AgentScoreEntity]:

        stmt = (
            select(AgentScoreModel)
            .where(
                AgentScoreModel.agent_id == agent_id
            )
            .order_by(
                AgentScoreModel.occurred_at.desc()
            )
        )

        result = await self._session.execute(stmt)

        models = result.scalars().all()

        return [
            AgentScoreMapper.to_entity(model)
            for model in models
        ]

    async def get_by_agent_id_and_date_range(
        self,
        agent_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> list[AgentScoreEntity]:

        stmt = (
            select(AgentScoreModel)
            .where(
                AgentScoreModel.agent_id == agent_id,
                AgentScoreModel.occurred_at >= start_date,
                AgentScoreModel.occurred_at <= end_date,
            )
            .order_by(
                AgentScoreModel.occurred_at.asc()
            )
        )

        result = await self._session.execute(stmt)

        models = result.scalars().all()

        return [
            AgentScoreMapper.to_entity(model)
            for model in models
        ]

    async def get_total_points_by_agent(
        self,
        agent_id: str,
    ) -> int:

        stmt = select(
            func.coalesce(
                func.sum(AgentScoreModel.points),
                0,
            )
        ).where(
            AgentScoreModel.agent_id == agent_id
        )

        result = await self._session.execute(stmt)

        return result.scalar_one()
