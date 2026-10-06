from abc import ABC,abstractmethod

class IRefreshTokenGenerator(ABC):

    @abstractmethod
    def generate(self, refresh_token_id) -> str:
        pass
