from abc import ABC, abstractmethod

from src.application.dto.team_dto import AddTeamMemberDTO, RemoveTeamMember, TeamResponseDTO, TeamCreateDTO, TeamUpdateDTO


class ITeamService(ABC):

    @abstractmethod
    async def get_by_id(
        self,
        team_id: str,
    ) -> TeamResponseDTO | None:
        pass

    @abstractmethod
    async def get_all(
        self,
    ) -> list[TeamResponseDTO]:
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
    ) -> TeamResponseDTO:
        pass

    @abstractmethod
    async def delete(
        self,
        team_id: str,
    ) -> None:
        pass

    @abstractmethod
    async def add_team_member(self, team_id : str, user_id: str) -> TeamResponseDTO: pass

    @abstractmethod
    async def remove_team_member(self, team_id : str, user_id : str) -> TeamResponseDTO: pass

