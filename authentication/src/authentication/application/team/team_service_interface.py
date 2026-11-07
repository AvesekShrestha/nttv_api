from abc import ABC, abstractmethod

from authentication.application.dto.team_dto import AddTeamMemberDTO, RemoveTeamMember, TeamDetailResponseDTO, TeamResponseDTO, TeamCreateDTO, TeamUpdateDTO
from authentication.application.dto.team_query_dto import TeamQueryDTO
from authentication.application.shared.pagination_response import PaginatedResponse
from authentication.application.dto.user_response_dto import UserResponseDTO


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
        query : TeamQueryDTO
    ) -> PaginatedResponse[TeamDetailResponseDTO] : 
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

    @abstractmethod
    async def get_by_ids(
        self,
        team_ids: list[str],
    ) -> list[TeamDetailResponseDTO]:
        pass


