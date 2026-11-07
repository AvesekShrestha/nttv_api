import httpx

from ticket.application.assignment.dto.team_data_dto import (
    TeamDetailResponseDTO,
    PaginatedResponseDTO,
)
from ticket.application.exceptions.organization_service_exceptions import (
    OrganizationServiceException,
)
from ticket.application.shared.organization_client_interface import (
    IOrganizationClient,
)


class OrganizationClient(IOrganizationClient):

    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client

    def _handle_http_error(self, exc: httpx.HTTPStatusError):
        try:
            error_data = exc.response.json()

            if isinstance(error_data, dict):
                message = error_data.get(
                    "message",
                    error_data.get("detail", "Organization service request failed"),
                )
            else:
                message = str(error_data)

        except ValueError:
            message = exc.response.text or "Organization service request failed"

        raise OrganizationServiceException(
            message=message,
            status=exc.response.status_code,
        ) from exc

    async def get_teams_by_category(
        self,
        category_id: str,
    ) -> list[TeamDetailResponseDTO]:

        try:
            response = await self.http_client.get(
                "/api/v1/team/",
                params={"category_id": category_id},
            )

            response.raise_for_status()

            data = PaginatedResponseDTO[
                TeamDetailResponseDTO
            ].model_validate(response.json())

            print(data.items)
            return data.items

        except httpx.HTTPStatusError as exc:
            self._handle_http_error(exc)

        except httpx.RequestError as exc:
            raise OrganizationServiceException(
                message="Unable to communicate with Organization service",
                status=503,
            ) from exc

    async def get_teams_by_id(
        self,
        teams_ids: list[str],
    ) -> list[TeamDetailResponseDTO]:

        try:
            response = await self.http_client.post(
                "/api/v1/team/bulk",
                json={"team_ids": teams_ids},
            )

            response.raise_for_status()

            return [
                TeamDetailResponseDTO.model_validate(team)
                for team in response.json()
            ]

        except httpx.HTTPStatusError as exc:
            self._handle_http_error(exc)

        except httpx.RequestError as exc:
            raise OrganizationServiceException(
                message="Unable to communicate with Organization service",
                status=503,
            ) from exc
