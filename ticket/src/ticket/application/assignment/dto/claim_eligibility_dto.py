from pydantic import BaseModel, ConfigDict


class ClaimEligibilityResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    can_claim: bool
    reason: str | None = None
