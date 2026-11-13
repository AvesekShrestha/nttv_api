from typing import Literal

from pydantic import BaseModel, Field


class TeamQueryDTO(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=5, ge=1, le=100)

    category_id: str | None = None
    level: str | None = None
    is_active: bool | None = None

    search: str | None = None

    sort_by: Literal[
        "name",
        "level",
        "created_at",
        "updated_at",
    ] = "created_at"

    sort_order: Literal["asc", "desc"] = "desc"
