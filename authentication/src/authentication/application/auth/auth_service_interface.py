from abc import ABC, abstractmethod

from authentication.application.dto.token_dto import AccessTokenResponseDTO
from authentication.application.dto.user_response_dto import UserResponseDTO
from authentication.application.dto.login_response_dto import LoginResponseDTO, LoginResultDTO
from authentication.application.dto.login_dto import LoginDTO
from authentication.application.dto.register_dto import RegisterDTO
from authentication.domain.users.user_aggregrate import UserAggregrate

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
