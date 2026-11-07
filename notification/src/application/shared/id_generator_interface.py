from abc import ABC, abstractmethod


class IIdGenerator(ABC):

    @abstractmethod
    def generate_notification_id(self) -> str:
        pass
