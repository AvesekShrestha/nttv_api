from abc import ABC, abstractmethod

from src.domain.team.team_aggregate import TeamAggregate


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
    ) -> list[TeamAggregate]:
        pass

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
