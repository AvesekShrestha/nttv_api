import httpx

from ticket.application.assignment.dto.team_data_dto import TeamDetailResponseDTO
from ticket.application.exceptions.organization_service_exceptions import OrganizationServiceException
from ticket.application.shared.organization_client_interface import IOrganizationClient

class OrganizationClient(IOrganizationClient):

    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client

    async def get_teams_by_category(
        self,
        category_id: str,
    ) -> list[TeamDetailResponseDTO]:

        try:
            response = await self.http_client.get(
                f"/api/v1/teams",
                params={
                    "category_id" : category_id
                }
            )

            response.raise_for_status()
            teams = [
                TeamDetailResponseDTO.model_validate(team)
                for team in response.json()
            ]
            return teams

        except httpx.HTTPStatusError as e:
            error_data = e.response.json()
            raise OrganizationServiceException(message=error_data.message, status=error_data.status)

    async def get_teams_by_id(self, teams_ids: list[str]) -> list[TeamDetailResponseDTO]:
        try:
            response = await self.http_client.post(
                f"/api/v1/teams/bulk",
                json={
                    "team_ids" : teams_ids
                }
            )

            response.raise_for_status()
            teams = [
                TeamDetailResponseDTO.model_validate(team)
                for team in response.json()
            ]
            return teams

        except httpx.HTTPStatusError as e:
            error_data = e.response.json()
            raise OrganizationServiceException(message=error_data.message, status=error_data.status)

