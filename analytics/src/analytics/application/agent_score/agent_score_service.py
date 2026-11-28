from analytics.application.agent_score.dto.agent_score_dto import (
    AgentScoreResponseDTO,
    AgentScoreSummaryResponseDTO,
)
from analytics.application.agent_score.agent_score_service_interface import (
    IAgentScoreService,
)
from analytics.application.interfaces.agent_score_repository_interface import (
    IAgentScoreRepository,
)


class AgentScoreService(IAgentScoreService):
    def __init__(
        self,
        agent_score_repository: IAgentScoreRepository,
    ):
        self._agent_score_repository = agent_score_repository

    async def get_scores_by_agent(
        self,
        agent_id: str,
    ) -> AgentScoreSummaryResponseDTO:
        entities = await self._agent_score_repository.get_by_agent_id(agent_id)
        total_points = await self._agent_score_repository.get_total_points_by_agent(
            agent_id
        )

        scores = [
            AgentScoreResponseDTO(
                id=e.id,
                agent_id=e.agent_id,
                ticket_id=e.ticket_id,
                source_event_id=e.source_event_id,
                activity_type=e.activity_type,
                points=e.points,
                occurred_at=e.occurred_at,
            )
            for e in entities
        ]

        return AgentScoreSummaryResponseDTO(
            agent_id=agent_id,
            total_points=total_points,
            scores=scores,
        )
