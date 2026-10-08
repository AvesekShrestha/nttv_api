from abc import ABC,abstractmethod

class IUnitOfWork(ABC):

    @abstractmethod
    async def commit(self) -> None:
        pass

    async def rollback(self) -> None: pass
