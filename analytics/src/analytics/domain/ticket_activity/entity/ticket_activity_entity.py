from datetime import datetime
from typing import Optional

from analytics.domain.shared.entity import Entity


class TicketActivityEntity(Entity[str]):

    def __init__(
        self,
        activity_id: str,
        source_event_id: str,
        ticket_id: str,
        activity_type: str,
        occurred_at: datetime,
        assignment_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        team_id: Optional[str] = None,
    ):
        super().__init__(activity_id)

        self._source_event_id = source_event_id
        self._ticket_id = ticket_id
        self._assignment_id = assignment_id
        self._actor_id = actor_id
        self._agent_id = agent_id
        self._team_id = team_id
        self._activity_type = activity_type
        self._occurred_at = occurred_at

    @staticmethod
    def create(
        activity_id: str,
        source_event_id: str,
        ticket_id: str,
        activity_type: str,
        occurred_at: datetime,
        assignment_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        team_id: Optional[str] = None,
    ) -> "TicketActivityEntity":

        return TicketActivityEntity(
            activity_id=activity_id,
            source_event_id=source_event_id,
            ticket_id=ticket_id,
            activity_type=activity_type,
            occurred_at=occurred_at,
            assignment_id=assignment_id,
            actor_id=actor_id,
            agent_id=agent_id,
            team_id=team_id,
        )

    @property
    def source_event_id(self) -> str:
        return self._source_event_id

    @property
    def ticket_id(self) -> str:
        return self._ticket_id

    @property
    def assignment_id(self) -> Optional[str]:
        return self._assignment_id

    @property
    def actor_id(self) -> Optional[str]:
        return self._actor_id

    @property
    def agent_id(self) -> Optional[str]:
        return self._agent_id

    @property
    def team_id(self) -> Optional[str]:
        return self._team_id

    @property
    def activity_type(self) -> str:
        return self._activity_type

    @property
    def occurred_at(self) -> datetime:
        return self._occurred_at
