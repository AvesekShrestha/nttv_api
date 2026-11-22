from urllib.parse import quote

import httpx
from pydantic import BaseModel, EmailStr, Field, ValidationError

from src.application.exceptions.recipient_lookup_exception import (
    RecipientLookupError,
    RecipientNotFoundError,
)
from src.application.shared.recipient_email_resolver_interface import (
    RecipientEmailResolverInterface,
)


class RecipientDetails(BaseModel):
    id: str = Field(min_length=1)
    email: EmailStr


class RecipientEmailClient(RecipientEmailResolverInterface):
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        *,
        access_token: str,
    ) -> None:
        if not access_token.strip():
            raise ValueError("An access token is required")

        self._http_client = http_client
        self._access_token = access_token

    async def get_email(self, user_id: str) -> str:
        if not user_id.strip():
            raise ValueError("user_id is required")

        path = f"/api/v1/user/{quote(user_id, safe='')}"

        try:
            response = await self._http_client.get(
                path,
                headers={
                    "Authorization": f"Bearer {self._access_token}",
                },
            )
        except httpx.RequestError as exc:
            raise RecipientLookupError(
                "Unable to reach authentication API"
            ) from exc

        if response.status_code == 404:
            raise RecipientNotFoundError(
                "Recipient does not exist"
            )

        if response.status_code in {401, 403}:
            raise RecipientLookupError(
                "Authentication API rejected lookup credentials"
            )

        if not response.is_success:
            raise RecipientLookupError(
                "Authentication API returned an unsuccessful status"
            )

        try:
            recipient = RecipientDetails.model_validate(
                response.json()
            )
        except (ValueError, ValidationError):
            raise RecipientLookupError(
                "Authentication API returned an invalid recipient"
            ) from None

        if recipient.id != user_id:
            raise RecipientLookupError(
                "Authentication API returned a different user ID"
            )

        return str(recipient.email)
