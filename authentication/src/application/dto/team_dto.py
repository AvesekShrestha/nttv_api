from dataclasses import dataclass
from datetime import date, datetime

from src.domain.shared.level import Level


@dataclass
class TeamMemberResponseDTO:
    id: str
    user_id: str
    joined_at: datetime | None
    is_active: bool


@dataclass
class TeamCreateDTO:
    name: str
    description: str
    category_id: str
    level: Level = Level.L1


@dataclass
class TeamUpdateDTO:
    name: str
    description: str
    category_id: str
    level: Level


@dataclass
class TeamResponseDTO:
    id: str
    name: str
    description: str
    level: Level
    category_id: str
    is_active: bool
    members: list[TeamMemberResponseDTO]
    created_at: datetime | None
    updated_at: datetime | None

@dataclass
class AddTeamMemberDTO:
    user_id : str

@dataclass
class RemoveTeamMember:
    user_id : str

