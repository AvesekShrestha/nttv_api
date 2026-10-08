from abc import ABC, abstractmethod

from src.application.dto.team_dto import AddTeamMemberDTO, RemoveTeamMember, TeamDetailResponseDTO, TeamResponseDTO, TeamCreateDTO, TeamUpdateDTO


class ITeamService(ABC):

    @abstractmethod
    async def get_by_id(
        self,
        team_id: str,
    ) -> TeamDetailResponseDTO | None:
        pass

    @abstractmethod
    async def get_all(
        self,
    ) -> list[TeamDetailResponseDTO]:
        pass

    @abstractmethod
    async def create(
        self,
        payload: TeamCreateDTO,
    ) -> TeamResponseDTO:
        pass

    @abstractmethod
    async def update(
        self,
        team_id: str,
        payload: TeamUpdateDTO,
    ) -> TeamDetailResponseDTO:
        pass

    @abstractmethod
    async def delete(
        self,
        team_id: str,
    ) -> bool:
        pass

    @abstractmethod
    async def add_team_member(self, team_id : str, user_id: str) -> TeamDetailResponseDTO: pass

    @abstractmethod
    async def remove_team_member(self, team_id : str, user_id : str) -> TeamDetailResponseDTO: pass

