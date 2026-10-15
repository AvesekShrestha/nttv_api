from pydantic import BaseModel, EmailStr, Field
from authentication.domain.shared.level import Level

class LoginDTO(BaseModel):
    email : EmailStr
    password : str = Field(min_length=8, description="Password must be atleast of 8 character")
