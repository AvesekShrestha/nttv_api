from abc import ABC, abstractmethod

from authentication.application.dto.create_staff_dto import CreateStaffDTO
from authentication.application.dto.user_response_dto import UserResponseDTO


class IUserService(ABC) : 

    @abstractmethod
    async def get_by_id(self, user_id: str) -> UserResponseDTO: 
        pass

    @abstractmethod
    async def get_all(self) -> list[UserResponseDTO]:
        pass

    @abstractmethod
    async def create_staff(self, payload : CreateStaffDTO) -> UserResponseDTO : pass 


