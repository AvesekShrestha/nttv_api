from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
)


class AuthEventModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        hide_input_in_errors=True,
    )


class OtpData(AuthEventModel):
    email: EmailStr
    otp: SecretStr = Field(min_length=1)


class AuthEvent(AuthEventModel):
    id: str = Field(min_length=1)
    key: str = Field(min_length=1)
    occurred_at: datetime
    data: OtpData
    published_at: datetime | None = None


class UserCreatedEvent(AuthEvent):
    event_type: Literal["user.created"]


class OtpResendEvent(AuthEvent):
    event_type: Literal["otp.resend"]
