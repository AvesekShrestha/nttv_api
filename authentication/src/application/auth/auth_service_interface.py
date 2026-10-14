from abc import ABC, abstractmethod

from application.dto.token_dto import AccessTokenResponseDTO
from application.dto.user_response_dto import UserResponseDTO
from application.dto.login_response_dto import LoginResponseDTO, LoginResultDTO
from application.dto.login_dto import LoginDTO
from application.dto.register_dto import RegisterDTO
from domain.users.user_aggregrate import UserAggregrate

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
