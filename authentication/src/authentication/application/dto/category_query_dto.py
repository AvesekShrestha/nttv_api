from typing import Literal

from pydantic import BaseModel, Field


class CategoryQueryDTO(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=5, ge=1, le=5)

    is_active: bool | None = None

    search: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    sort_by: Literal[
        "name",
        "created_at",
        "updated_at",
    ] = "created_at"

    sort_order: Literal["asc", "desc"] = "desc"
