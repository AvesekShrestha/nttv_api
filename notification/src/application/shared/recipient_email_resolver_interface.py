from abc import ABC, abstractmethod


class RecipientEmailResolverInterface(ABC):
    @abstractmethod
    async def get_email(self, user_id: str) -> str:
        pass
