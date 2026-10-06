from datetime import datetime
from dataclasses import dataclass

@dataclass
class UserResponseDTO:
    id: str
    username: str
    email: str
    role: str
    level: str | None
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None 
