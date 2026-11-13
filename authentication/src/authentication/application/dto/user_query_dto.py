from typing import Literal

from pydantic import BaseModel, Field

from authentication.domain.users.user_role import UserRole


class UserQueryDTO(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=5, ge=1, le=100)

    role: UserRole | None = None
    level: str | None = Field(default=None, max_length=2)
    is_active: bool | None = None

    search: str | None = Field(
        default=None,
        min_length=1,
        max_length=254,
    )

    sort_by: Literal[
        "username",
        "email",
        "role",
        "level",
        "created_at",
        "updated_at",
    ] = "created_at"

    sort_order: Literal["asc", "desc"] = "desc"
