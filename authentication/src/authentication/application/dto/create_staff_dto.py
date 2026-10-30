from pydantic import BaseModel, EmailStr

from authentication.domain.shared.level import Level
from authentication.domain.users.user_role import UserRole

class CreateStaffDTO(BaseModel):
    username: str
    email : EmailStr
    password : str
    role : UserRole
    level : Level


