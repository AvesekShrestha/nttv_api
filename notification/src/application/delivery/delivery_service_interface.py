from abc import ABC, abstractmethod


class DeliveryServiceInterface(ABC):
    @abstractmethod
    async def deliver(self, notification_id: str) -> None:
        pass
