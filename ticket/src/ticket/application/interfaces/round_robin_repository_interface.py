from abc import ABC, abstractmethod

from ticket.domain.rotation.round_robin_aggregate import RoundRobinAggregate


class IRoundRobinRepository(ABC) : 

    @abstractmethod
    async def get_by_scope(self, scope_type : str, scope_id : str) -> RoundRobinAggregate | None : pass


    @abstractmethod
    async def add(self, aggregate : RoundRobinAggregate)-> None : 
        pass

    @abstractmethod
    async def update(self, aggregate : RoundRobinAggregate) -> None : 
        pass

