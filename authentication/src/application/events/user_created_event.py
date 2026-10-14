from dataclasses import dataclass
from pydantic import BaseModel

class UserCreatedEvent(BaseModel):
    email: str
    role : str
