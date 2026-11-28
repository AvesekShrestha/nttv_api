from datetime import datetime
from typing import Optional

from analytics.config import settings
from analytics.domain.shared.aggregate import AggregrateRoot
from analytics.domain.analytics_event.analytics_event_status import AnalyticsEventStatus



class AnalyticsEventAggregate(AggregrateRoot[str]):

    def __init__(
        self,
        id: str,
        event_id: str,
        event_type: str,
        payload: dict,
        status: AnalyticsEventStatus = AnalyticsEventStatus.PENDING,
        attempts: int = 0,
        last_error: Optional[str] = None,
        next_retry_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        processed_at: Optional[datetime] = None,
    ):
        self._id = id
        self._event_id = event_id
        self._event_type = event_type
        self._payload = payload
        self._status = status
        self._attempts = attempts
        self._last_error = last_error
        self._next_retry_at = next_retry_at
        self._created_at = created_at or datetime.now()
        self._processed_at = processed_at

    @classmethod
    def create(
        cls,
        id: str,
        event_id: str,
        event_type: str,
        payload: dict,
    ) -> "AnalyticsEventAggregate":

        return cls(
            id=id,
            event_id=event_id,
            event_type=event_type,
            payload=payload,
        )

    @property
    def id(self) -> str:
        return self._id

    @property
    def event_id(self) -> str:
        return self._event_id

    @property
    def event_type(self) -> str:
        return self._event_type

    @property
    def payload(self) -> dict:
        return self._payload

    @property
    def status(self) -> AnalyticsEventStatus:
        return self._status

    @property
    def attempts(self) -> int:
        return self._attempts

    @property
    def last_error(self) -> Optional[str]:
        return self._last_error

    @property
    def next_retry_at(self) -> Optional[datetime]:
        return self._next_retry_at

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def processed_at(self) -> Optional[datetime]:
        return self._processed_at

    @property
    def is_processed(self) -> bool:
        return self._status == AnalyticsEventStatus.PROCESSED

    def mark_as_processing(self) -> None:
        if self._status not in (
            AnalyticsEventStatus.PENDING,
            AnalyticsEventStatus.FAILED,
        ):
            raise ValueError("Event cannot be processed in its current state")

        self._status = AnalyticsEventStatus.PROCESSING
        self._attempts += 1
        self._last_error = None
        self._next_retry_at = None

    def mark_as_processed(self, now: datetime) -> None:

        if self._status != AnalyticsEventStatus.PROCESSING:
            raise ValueError(
                "Only processing events can be marked as processed"
            )

        self._status = AnalyticsEventStatus.PROCESSED
        self._processed_at = now
        self._last_error = None
        self._next_retry_at = None

    def mark_as_failed(
        self,
        error: str,
        next_retry_at: datetime | None = None,
    ) -> None:

        if self._status != AnalyticsEventStatus.PROCESSING:
            raise ValueError(
                "Only processing events can be marked as failed"
            )

        self._last_error = error

        if self._attempts >= settings.MAX_RETRY_ATTEMPTS:
            self._status = AnalyticsEventStatus.DEAD_LETTER
            self._next_retry_at = None
            return

        self._status = AnalyticsEventStatus.FAILED
        self._next_retry_at = next_retry_at
