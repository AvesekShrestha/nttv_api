from datetime import datetime
from pydantic import BaseModel

class TeamMemberResponseDTO(BaseModel):
    id: str
    user_id: str
    joined_at: datetime | None
    is_active: bool


class TeamDetailResponseDTO(BaseModel):
    id: str
    name: str
    description: str
    level: str 
    category_id: str
    is_active: bool
    members: list[TeamMemberResponseDTO]
    created_at: datetime | None
    updated_at: datetime | None
