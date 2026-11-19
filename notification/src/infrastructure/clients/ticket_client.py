from typing import TypeVar
from urllib.parse import quote

import httpx
from pydantic import BaseModel

from src.application.dto.ticket_data_dto import (
    AssignmentDetails,
    TicketDetails,
)
from src.application.exceptions.ticket_service_exception import (
    TicketServiceError,
)
from src.application.shared.ticket_client_interface import (
    TicketClientInterface,
)


ResponseModel = TypeVar("ResponseModel", bound=BaseModel)


class TicketClient(TicketClientInterface):
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client

    async def get_ticket(self, ticket_id: str) -> TicketDetails:
        if not ticket_id.strip():
            raise ValueError("ticket_id is required")

        ticket = await self._get(
            f"/api/v1/ticket/{quote(ticket_id, safe='')}",
            TicketDetails,
        )

        if ticket.id != ticket_id:
            raise TicketServiceError(
                "Ticket API returned a different ticket ID"
            )

        return ticket

    async def get_assignment(
        self,
        assignment_id: str,
    ) -> AssignmentDetails:
        if not assignment_id.strip():
            raise ValueError("assignment_id is required")

        assignment = await self._get(
            f"/api/v1/assignment/{quote(assignment_id, safe='')}",
            AssignmentDetails,
        )

        if assignment.id != assignment_id:
            raise TicketServiceError(
                "Ticket API returned a different assignment ID"
            )

        return assignment

    async def _get(
        self,
        path: str,
        response_model: type[ResponseModel],
    ) -> ResponseModel:
        try:
            response = await self.http_client.get(path)
            response.raise_for_status()

        except httpx.HTTPStatusError as exc:
            raise TicketServiceError(
                "Ticket API returned an unsuccessful status",
                status_code=exc.response.status_code,
            ) from exc

        except httpx.RequestError as exc:
            raise TicketServiceError(
                "Unable to reach Ticket API"
            ) from exc

        try:
            return response_model.model_validate(response.json())

        except ValueError:
            raise TicketServiceError(
                "Ticket API returned an invalid response",
                status_code=response.status_code,
            ) from None
