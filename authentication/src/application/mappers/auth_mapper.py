from src.application.dto.login_response_dto import LoginResponseDTO, LoginResultDTO
from src.application.mappers.user_mapper import UserMapper
from src.application.dto.user_response_dto import UserResponseDTO
from src.domain.users.user_aggregrate import UserAggregrate


class AuthMapper:

    @staticmethod
    def login_response(aggregate : UserAggregrate, access_token : str, refresh_token: str) -> LoginResultDTO:
        return LoginResultDTO(
            user=UserMapper.to_response(aggregate),
            access_token=access_token,
            refresh_token=refresh_token
        )
