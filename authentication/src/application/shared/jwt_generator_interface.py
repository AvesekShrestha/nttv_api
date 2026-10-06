from abc import ABC, abstractmethod

from src.application.shared.jwt_payload import JWTPayload

class IJWTGenerator(ABC):
    
    @abstractmethod
    async def generate(self, payload : JWTPayload) -> str: pass

    @abstractmethod
    async def verify(self, token : str) -> JWTPayload : pass
