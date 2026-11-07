from abc import ABC, abstractmethod

from authentication.application.dto.create_staff_dto import CreateStaffDTO
from authentication.application.dto.user_query_dto import UserQueryDTO
from authentication.application.dto.user_response_dto import UserResponseDTO
from authentication.application.shared.pagination_response import PaginatedResponse


class IUserService(ABC) : 

    @abstractmethod
    async def get_by_id(self, user_id: str) -> UserResponseDTO: 
        pass

    @abstractmethod
    async def get_all(self, query : UserQueryDTO) -> PaginatedResponse[UserResponseDTO]:
        pass

    @abstractmethod
    async def create_staff(self, payload : CreateStaffDTO) -> UserResponseDTO : pass 


