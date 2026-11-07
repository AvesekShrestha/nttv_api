from abc import ABC, abstractmethod

from ticket.application.assignment.dto.team_data_dto import TeamDetailResponseDTO

class IOrganizationClient(ABC):

    @abstractmethod
    async def get_teams_by_category(
        self,
        category_id: str,
    ) -> list[TeamDetailResponseDTO]:
        pass

    @abstractmethod
    async def get_teams_by_id(
            self,
            teams_ids : list[str]
    ) -> list[TeamDetailResponseDTO]: pass

