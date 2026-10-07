from dataclasses import dataclass
from datetime import datetime


@dataclass
class CategoryCreateDTO:
    name: str
    description: str


@dataclass
class CategoryUpdateDTO:
    name: str
    description: str


@dataclass
class CategoryResponseDTO:
    id: str
    name: str
    description: str
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None
