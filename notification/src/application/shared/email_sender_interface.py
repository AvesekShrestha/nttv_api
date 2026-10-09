from abc import ABC, abstractmethod


class EmailSenderInterface(ABC):
    @abstractmethod
    async def send(self, to: str, subject: str, body: str) -> None:
        pass
