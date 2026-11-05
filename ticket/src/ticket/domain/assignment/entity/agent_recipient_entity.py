from dataclasses import dataclass
from datetime import datetime

from ticket.domain.assignment.exceptions.agent_exceptions import AlreadyClaimed, NotEligiableToClaim
from ticket.domain.shared.entity import Entity


@dataclass
class AgentRecipientEntity(Entity[str]):
    _team_recipient_id: str
    _agent_id: str
    _can_claim: bool = False
    _notified_at: datetime | None = None
    _acknowledged_at: datetime | None = None
    _claimed_at: datetime | None = None
    _created_at: datetime | None = None

    @property
    def team_recipient_id(self) -> str:
        return self._team_recipient_id

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

    @property
    def created_at(self) -> datetime | None:
        return self._created_at

    def mark_notified(self, at: datetime) -> None:
        if self._notified_at is None:
            self._notified_at = at

    def acknowledge(self, at: datetime) -> None:
        if self._acknowledged_at is None:
            self._acknowledged_at = at

    def enable_claiming(self) -> None:
        if self.claimed_at is not None : raise AlreadyClaimed("You have already claimed the ticket")

        if self._claimed_at is None:
            self._can_claim = True

    def disable_claiming(self) -> None:
        self._can_claim = False

    def claim(self, at: datetime) -> None:
        if self._claimed_at is not None:
            raise AlreadyClaimed(
                "Agent has already claimed this assignment"
            )

        if not self._can_claim:
            raise NotEligiableToClaim(
                "Agent is not eligible to claim this assignment"
            )

        self._claimed_at = at
        self._can_claim = False

    @staticmethod
    def create(
        id: str,
        team_recipient_id: str,
        agent_id: str,
        can_claim: bool = False,
        created_at: datetime | None = None,
    ) -> AgentRecipientEntity:
        return AgentRecipientEntity(
            _id=id,
            _team_recipient_id=team_recipient_id,
            _agent_id=agent_id,
            _can_claim=can_claim,
            _created_at=created_at,
        )
