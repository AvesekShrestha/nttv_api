from abc import ABC, abstractmethod

from authentication.application.shared.pagination_response import PaginatedResponse
from authentication.application.dto.team_query_dto import TeamQueryDTO

from authentication.domain.team.team_aggregate import TeamAggregate

class ITeamRepository(ABC):

    @abstractmethod
    async def get_by_id(
        self,
        team_id: str,
    ) -> TeamAggregate | None:
        pass

    @abstractmethod
    async def get_all(
        self,
        query : TeamQueryDTO
    ) -> PaginatedResponse[TeamAggregate]:
        pass

    @abstractmethod
    async def get_by_ids(
        self,
        team_ids : list[str]
    ) -> list[TeamAggregate] : pass

    @abstractmethod
    async def add(
        self,
        aggregate: TeamAggregate,
    ) -> TeamAggregate:
        pass

    @abstractmethod
    async def update(
        self,
        aggregate: TeamAggregate,
    ) -> TeamAggregate:
        pass

    @abstractmethod
    async def delete(
        self,
        team_id: str,
    ) -> None:
        pass

