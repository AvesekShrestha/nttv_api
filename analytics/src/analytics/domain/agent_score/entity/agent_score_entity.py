from datetime import datetime

from analytics.domain.shared.entity import Entity


class AgentScoreEntity(Entity[str]):

    def __init__(
        self,
        score_id: str,
        agent_id: str | None,
        ticket_id: str,
        source_event_id: str,
        activity_type: str,
        points: int,
        occurred_at: datetime,
    ):
        super().__init__(score_id)

        self._agent_id = agent_id
        self._ticket_id = ticket_id
        self._source_event_id = source_event_id
        self._activity_type = activity_type
        self._points = points
        self._occurred_at = occurred_at

    @staticmethod
    def create(
        score_id: str,
        agent_id: str,
        ticket_id: str,
        source_event_id: str,
        activity_type: str,
        points: int,
        occurred_at: datetime,
    ) -> "AgentScoreEntity":

        return AgentScoreEntity(
            score_id=score_id,
            agent_id=agent_id,
            ticket_id=ticket_id,
            source_event_id=source_event_id,
            activity_type=activity_type,
            points=points,
            occurred_at=occurred_at,
        )

    @property
    def agent_id(self) -> str | None:
        return self._agent_id

    @property
    def ticket_id(self) -> str:
        return self._ticket_id

    @property
    def source_event_id(self) -> str:
        return self._source_event_id

    @property
    def activity_type(self) -> str:
        return self._activity_type

    @property
    def points(self) -> int:
        return self._points

    @property
    def occurred_at(self) -> datetime:
        return self._occurred_at
