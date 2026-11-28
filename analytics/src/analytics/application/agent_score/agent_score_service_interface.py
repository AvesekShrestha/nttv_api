from abc import ABC, abstractmethod
from analytics.application.agent_score.dto.agent_score_dto import (
    AgentScoreResponseDTO,
    AgentScoreSummaryResponseDTO,
)


class IAgentScoreService(ABC):
    @abstractmethod
    async def get_scores_by_agent(
        self,
        agent_id: str,
    ) -> AgentScoreSummaryResponseDTO:
        pass
