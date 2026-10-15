from pydantic import BaseModel, EmailStr, Field

from authentication.domain.shared.level import Level

class RegisterDTO(BaseModel):
    username : str = Field(min_length=1, description="Username must be of atleast 1 character")
    email : EmailStr
    password : str = Field(min_length=8, description="Password must be atleast of 8 character")
