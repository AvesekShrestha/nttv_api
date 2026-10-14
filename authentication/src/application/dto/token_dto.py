from datetime import datetime
from dataclasses import dataclass

from src.application.dto.user_response_dto import UserResponseDTO

@dataclass(frozen=True)
class AccessTokenResponseDTO:
    access_token : str
