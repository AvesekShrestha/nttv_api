from datetime import datetime
from typing import Optional

from analytics.domain.shared.entity import Entity
from analytics.domain.ticket_analytics.ticket_status import TicketStatus


class TicketAnalyticsEntity(Entity[str]):

    def __init__(
        self,
        ticket_id: str,
        category_id: str,
        created_by: str,
        priority: str,
        current_status: str,
        created_at: datetime,
        resolved_at: Optional[datetime] = None,
        resolution_duration_seconds: Optional[int] = None,
    ):
        super().__init__(ticket_id)

        self._category_id = category_id
        self._created_by = created_by
        self._priority = priority
        self._current_status = current_status
        self._created_at = created_at
        self._resolved_at = resolved_at
        self._resolution_duration_seconds = resolution_duration_seconds

    @staticmethod
    def create(
        ticket_id: str,
        category_id: str,
        created_by: str,
        priority: str,
        current_status: str,
        created_at: datetime,
        resolved_at: Optional[datetime] = None,
        resolution_duration_seconds: Optional[int] = None,
    ) -> "TicketAnalyticsEntity":

        return TicketAnalyticsEntity(
            ticket_id=ticket_id,
            category_id=category_id,
            created_by=created_by,
            priority=priority,
            current_status=current_status,
            created_at=created_at,
            resolved_at=resolved_at,
            resolution_duration_seconds=resolution_duration_seconds,
        )

    @property
    def category_id(self) -> str:
        return self._category_id

    @property
    def created_by(self) -> str:
        return self._created_by

    @property
    def priority(self) -> str:
        return self._priority

    @property
    def current_status(self) -> str:
        return self._current_status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def resolved_at(self) -> Optional[datetime]:
        return self._resolved_at

    @property
    def resolution_duration_seconds(self) -> Optional[int]:
        return self._resolution_duration_seconds

    def update_status(self, status: TicketStatus) -> None:
        self._current_status = status.value

    def update_resolution_duration_seconds(self, seconds : int) -> None: 
        self._resolution_duration_seconds = seconds
