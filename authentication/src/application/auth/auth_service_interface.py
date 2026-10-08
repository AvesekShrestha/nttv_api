from abc import ABC, abstractmethod

from src.application.dto.token_dto import AccessTokenResponseDTO
from src.application.dto.user_response_dto import UserResponseDTO
from src.application.dto.login_response_dto import LoginResponseDTO, LoginResultDTO
from src.application.dto.login_dto import LoginDTO
from src.application.dto.register_dto import RegisterDTO
from src.domain.users.user_aggregrate import UserAggregrate

class IAuthService(ABC):

    @abstractmethod
    async def register(
        self,
        payload: RegisterDTO,
    ) -> UserResponseDTO:
        pass

    @abstractmethod
    async def login(
        self,
        payload: LoginDTO,
    ) -> LoginResultDTO:
        pass

    @abstractmethod
    async def logout(self, refresh_token: str) -> bool : pass

    @abstractmethod
    async def refresh(self, refresh_token: str) -> AccessTokenResponseDTO : pass
