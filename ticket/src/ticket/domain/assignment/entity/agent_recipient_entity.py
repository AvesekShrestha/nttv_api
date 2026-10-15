from dataclasses import dataclass
from datetime import datetime

from ticket.domain.shared.entity import Entity


@dataclass
class AgentRecipientEntity(Entity[str]):
    _agent_id: str
    _can_claim: bool = False
    _notified_at: datetime | None = None
    _acknowledged_at: datetime | None = None
    _claimed_at: datetime | None = None

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def can_claim(self) -> bool:
        return self._can_claim

    @property
    def notified_at(self) -> datetime | None:
        return self._notified_at

    @property
    def acknowledged_at(self) -> datetime | None:
        return self._acknowledged_at

    @property
    def claimed_at(self) -> datetime | None:
        return self._claimed_at

    def mark_notified(self, at: datetime) -> None:
        if self._notified_at is None:
            self._notified_at = at

    def acknowledge(self, at: datetime) -> None:
        if self._acknowledged_at is None:
            self._acknowledged_at = at

    def enable_claiming(self) -> None:
        if self._claimed_at is None:
            self._can_claim = True

    def disable_claiming(self) -> None:
        self._can_claim = False

    def claim(self, at: datetime) -> None:
        if not self._can_claim:
            raise ValueError("Agent is not eligible to claim this assignment")

        if self._claimed_at is not None:
            raise ValueError("Agent has already claimed this assignment")

        self._claimed_at = at
        self._can_claim = False
