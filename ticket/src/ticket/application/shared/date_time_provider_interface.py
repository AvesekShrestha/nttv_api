from abc import ABC, abstractmethod
from datetime import datetime

class IDateTimeProvider(ABC):

    @abstractmethod
    def now(self) -> datetime: pass
