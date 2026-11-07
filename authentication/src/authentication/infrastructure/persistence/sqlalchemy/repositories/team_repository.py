from sqlalchemy import delete, select, func, or_, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from authentication.application.dto.team_query_dto import TeamQueryDTO
from authentication.application.interfaces.team_repository_interface import ITeamRepository
from authentication.application.shared.pagination_response import PaginatedResponse
from authentication.domain.team.team_aggregate import TeamAggregate
from authentication.infrastructure.persistence.sqlalchemy.mappers.team_infrastructure_mapper import TeamMapper
from authentication.infrastructure.persistence.sqlalchemy.models.team_model import Team

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

    async def get_by_ids(self, team_ids: list[str]) -> list[TeamAggregate]:

        query = (
            select(Team)
            .options(selectinload(Team.members))
            .where(Team.id.in_(team_ids))
        )

        result = await self.session.execute(query)
        teams = result.scalars().all()

        return[
            TeamMapper.to_domain_with_members(team)
            for team in teams
        ]

    async def get_all(
        self,
        query: TeamQueryDTO,
    ) -> PaginatedResponse[TeamAggregate]:

        filters = []

        if query.category_id is not None:
            filters.append(
                Team.category_id == query.category_id
            )

        if query.level is not None:
            filters.append(
                Team.level == query.level
            )

        if query.is_active is not None:
            filters.append(
                Team.is_active == query.is_active
            )

        if query.search is not None and query.search.strip():
            search_term = f"%{query.search.strip()}%"

            filters.append(
                or_(
                    Team.name.ilike(search_term),
                    Team.description.ilike(search_term),
                )
            )

        count_stmt = (
            select(func.count())
            .select_from(Team)
            .where(*filters)
        )

        total = await self.session.scalar(count_stmt)

        sort_columns = {
            "name": Team.name,
            "level": Team.level,
            "created_at": Team.created_at,
            "updated_at": Team.updated_at,
        }

        sort_column = sort_columns[query.sort_by]

        if query.sort_order == "asc":

            ordering = asc(sort_column)
        else:
            ordering = desc(sort_column)

        offset = (query.page - 1) * query.limit

        stmt = (
            select(Team)
            .options(selectinload(Team.members))
            .where(*filters)
            .order_by(ordering, Team.id)
            .offset(offset)
            .limit(query.limit)
        )

        result = await self.session.execute(stmt)

        teams = result.scalars().all()

        return PaginatedResponse(
            items=[
                TeamMapper.to_domain_with_members(model=team)
                for team in teams
            ],
            total=total or 0,
            page=query.page,
            limit=query.limit,
        )


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
