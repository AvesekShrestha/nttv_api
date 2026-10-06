import strawberry
from datetime import datetime

@strawberry.type
class UserType:
    id: str
    username: str
    email: str
    level: str | None
    role: str
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None
