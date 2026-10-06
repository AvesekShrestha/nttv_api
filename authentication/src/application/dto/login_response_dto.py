from datetime import datetime
from dataclasses import dataclass

from src.application.dto.user_response_dto import UserResponseDTO

@dataclass(frozen=True)
class LoginResponseDTO:
    user : UserResponseDTO
    access_token : str
    refresh_token : str
