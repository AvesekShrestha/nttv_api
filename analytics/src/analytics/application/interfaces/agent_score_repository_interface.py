from abc import ABC, abstractmethod
from datetime import datetime

from analytics.domain.agent_score.entity.agent_score_entity import (
    AgentScoreEntity,
)


class IAgentScoreRepository(ABC):

    @abstractmethod
    async def save(
        self,
        score: AgentScoreEntity,
    ) -> None:
        pass

    @abstractmethod
    async def get_by_source_event_id(
        self,
        source_event_id: str,
    ) -> AgentScoreEntity | None:
        pass

    @abstractmethod
    async def get_by_agent_id(
        self,
        agent_id: str,
    ) -> list[AgentScoreEntity]:
        pass

    @abstractmethod
    async def get_by_agent_id_and_date_range(
        self,
        agent_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> list[AgentScoreEntity]:
        pass

    @abstractmethod
    async def get_total_points_by_agent(
        self,
        agent_id: str,
    ) -> int:
        pass
