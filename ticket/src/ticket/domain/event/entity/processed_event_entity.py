from dataclasses import dataclass
from datetime import datetime

from ticket.domain.shared.entity import Entity


@dataclass
class ProcessedEventEntity(Entity[str]):

    _event_id: str
    _event_type: str
    _processed_at: datetime

    @classmethod
    def create(
        cls,
        event_id: str,
        event_type: str,
        processed_at: datetime
    ) -> "ProcessedEventEntity":

        return ProcessedEventEntity(
            _id=event_id,
            _event_id=event_id,
            _event_type=event_type,
            _processed_at=processed_at
        )

    @property
    def event_id(self) -> str:
        return self._event_id

    @property
    def event_type(self) -> str:
        return self._event_type

    @property
    def processed_at(self) -> datetime:
        return self._processed_at
