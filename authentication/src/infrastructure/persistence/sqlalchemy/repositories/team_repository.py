from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.application.interfaces.team_repository_interface import ITeamRepository
from src.domain.team.team_aggregate import TeamAggregate
from src.infrastructure.persistence.sqlalchemy.mappers.team_infrastructure_mapper import TeamMapper
from src.infrastructure.persistence.sqlalchemy.models.team_model import Team

class TeamRepository(ITeamRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        team_id: str,
    ) -> TeamAggregate | None:

        stmt = (
            select(Team)
            .where(Team.id == team_id)
            .options(selectinload(Team.members))
        )

        result = await self.session.execute(stmt)

        team = result.scalar_one_or_none()

        if team is None:
            return None

        return TeamMapper.to_domain_with_members(team)

    async def get_all(
        self,
    ) -> list[TeamAggregate]:

        stmt = (
            select(Team)
            .options(selectinload(Team.members))
        )

        result = await self.session.execute(stmt)

        teams = result.scalars().all()

        return [
            TeamMapper.to_domain_with_members(team)
            for team in teams
        ]

    async def add(
        self,
        aggregate: TeamAggregate,
    ) -> TeamAggregate:

        team = TeamMapper.to_model(aggregate)

        self.session.add(team)

        await self.session.flush()

        return TeamMapper.to_domain(team)

    async def update(
        self,
        aggregate: TeamAggregate,
    ) -> TeamAggregate:

        team = TeamMapper.to_model(aggregate)
        updated_team = await self.session.merge(team)

        await self.session.flush()

        return TeamMapper.to_domain_with_members(updated_team)

    async def delete(
        self,
        team_id: str,
    ) -> None:

        stmt = delete(Team).where(
            Team.id == team_id
        )

        await self.session.execute(stmt)

        await self.session.flush()
