from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.domain.shared.entity import Entity

@dataclass
class OutboxEvent(Entity[str]):

    _event_type: str
    _occurred_at: datetime
    _data: dict[str, Any]
    _published_at: datetime | None = None

    @property
    def id(self) -> str:
        return self._id

    @property
    def event_type(self) -> str:
        return self._event_type

    @property
    def occurred_at(self) -> datetime:
        return self._occurred_at

    @property
    def data(self) -> dict[str, Any]:
        return self._data

    @property
    def published_at(self) -> datetime | None:
        return self._published_at

    @staticmethod
    def create(
        event_id: str,
        event_type: str,
        occurred_at: datetime,
        data: dict[str, Any],
    ) -> "OutboxEvent":

        return OutboxEvent(
            _id=event_id,
            _event_type=event_type,
            _occurred_at=occurred_at,
            _data=data
        )

    def mark_published(self, published_at: datetime) -> None:
        self._published_at = published_at
