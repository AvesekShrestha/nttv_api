from dataclasses import dataclass, field
from datetime import datetime

from ticket.application.assignment.exceptions.index import AgentNotFound
from ticket.domain.assignment.exceptions.agent_exceptions import AgentAlreadyExists, AlreadyClaimed, NotAvailableToClaim
from ticket.domain.assignment.exceptions.assignment_exception import AlreadyAcknowledged, AssignmentAlreadyStarted, AssignmentAlreadyTerminated, AssignmentIncompletable
from ticket.domain.assignment.exceptions.team_recipient_exception import InvalidRequest, TeamAlreadyExists
from ticket.domain.shared.aggregate import AggregrateRoot
from ticket.domain.assignment.assignment_type import AssignmentType
from ticket.domain.assignment.assignment_status import AssignmentStatus
from ticket.domain.assignment.entity.team_recipient_entity import (
    TeamRecipientEntity,
)

@dataclass
class AssignmentAggregate(AggregrateRoot[str]):
    _ticket_id: str
    _assignment_type: AssignmentType

    _status: AssignmentStatus = AssignmentStatus.PENDING
    _primary_agent_id: str | None = None
    _responsible_agent_id: str | None = None

    _team_recipients: list[TeamRecipientEntity] = field(
        default_factory=list
    )

    _assigned_at: datetime | None = None
    _acknowledgment_deadline_at: datetime | None = None
    _resolution_deadline_at: datetime | None = None

    _acknowledgment_sla_breached_at: datetime | None = None
    _resolution_sla_breached_at: datetime | None = None

    _assigned_by: str | None = None
    _acknowledged_at: datetime | None = None
    _completed_at: datetime | None = None
    _created_at: datetime | None = None
    _updated_at: datetime | None = None

    @property
    def ticket_id(self) -> str:
        return self._ticket_id

    @property
    def assigned_by(self) -> str | None:
        return self._assigned_by

    @property
    def assignment_type(self) -> AssignmentType:
        return self._assignment_type

    @property
    def status(self) -> AssignmentStatus:
        return self._status

    @property
    def primary_agent_id(self) -> str | None:
        return self._primary_agent_id

    @property
    def responsible_agent_id(self) -> str | None:
        return self._responsible_agent_id

    @property
    def team_recipients(self) -> list[TeamRecipientEntity]:
        return self._team_recipients.copy()

    @property
    def assigned_at(self) -> datetime | None:
        return self._assigned_at

    @property
    def acknowledged_at(self) -> datetime | None:
        return self._acknowledged_at

    @property
    def completed_at(self) -> datetime | None:
        return self._completed_at

    @property
    def created_at(self) -> datetime | None:
        return self._created_at

    @property
    def updated_at(self) -> datetime | None:
        return self._updated_at

    @property
    def acknowledgment_deadline_at(self) -> datetime | None:
        return self._acknowledgment_deadline_at

    @property
    def resolution_deadline_at(self) -> datetime | None:
        return self._resolution_deadline_at

    @property
    def acknowledgment_sla_breached_at(self) -> datetime | None:
        return self._acknowledgment_sla_breached_at

    @property
    def resolution_sla_breached_at(self) -> datetime | None:
        return self._resolution_sla_breached_at

    @staticmethod
    def create(
        id: str,
        ticket_id: str,
        assignment_type: AssignmentType,
        assigned_at: datetime,
        assigned_by: str | None = None,
        acknowledgment_deadline_at: datetime | None = None,
        resolution_deadline_at: datetime | None = None,
        primary_agent_id: str | None = None,
        responsible_agent_id : str | None = None
    ) -> AssignmentAggregate:

        return AssignmentAggregate(
            _id=id,
            _ticket_id=ticket_id,
            _assignment_type=assignment_type,
            _assigned_by=assigned_by,
            _primary_agent_id=primary_agent_id,
            _responsible_agent_id=responsible_agent_id,
            _assigned_at=assigned_at,
            _acknowledgment_deadline_at=acknowledgment_deadline_at,
            _resolution_deadline_at=resolution_deadline_at,
            _created_at=assigned_at,
            _updated_at=assigned_at,
        )

    def _touch(self, at: datetime) -> None:
        self._updated_at = at

    def _is_terminal(self) -> bool:
        return self._status in {
            AssignmentStatus.COMPLETED,
            AssignmentStatus.CANCELLED,
            AssignmentStatus.SUPERSEDED,
        }

    def _find_agent(self, agent_id: str):
        for team in self._team_recipients:
            agent = team.get_agent(agent_id)

            if agent is not None:
                return agent

        return None

    def _disable_all_claims(self) -> None:
        for team in self._team_recipients:
            for agent in team.agents:
                agent.disable_claiming()


    def _enable_all_claims(self) -> None:
        for team_recipient in self._team_recipients:
            for agent_recipient in team_recipient.agents:
                agent_recipient.enable_claiming()

    def add_team_recipient(
        self,
        recipients: list[TeamRecipientEntity],
    ) -> None:
        if self._status != AssignmentStatus.PENDING:
            raise InvalidRequest(
                "Recipients can only be added to a pending assignment"
            )

        existing_team_ids = {
            team.team_id
            for team in self._team_recipients
        }

        incoming_team_ids = set()

        for recipient in recipients:
            if recipient.assignment_id != self.id:
                raise InvalidRequest(
                    "Team recipient belongs to a different assignment"
                )

            if (
                recipient.team_id in existing_team_ids
                or recipient.team_id in incoming_team_ids
            ):
                raise TeamAlreadyExists(
                    "Team already added to this assignment"
                )

            incoming_team_ids.add(recipient.team_id)

        for recipient in recipients:
            self._team_recipients.append(recipient)

    def acknowledge(
        self,
        agent_id: str,
        at: datetime,
    ) -> None:
        if self._is_terminal():
            raise AssignmentAlreadyTerminated(
                "A terminal assignment cannot be acknowledged"
            )

        agent = self._find_agent(agent_id)

        if agent is None:
            raise AgentNotFound(
                "Agent is not a recipient of this assignment"
            )

        if agent.acknowledged_at is not None:
            raise AlreadyAcknowledged("Ticket already acknowledged")

        agent.acknowledge(at)
        agent.mark_notified(at)
        agent.claim(at)

        if self._acknowledged_at is None:
            self._acknowledged_at = at

        self._status = AssignmentStatus.IN_PROGRESS
        self._responsible_agent_id=agent_id
        self._disable_all_claims()


        self._touch(at)

    def mark_acknowledgment_sla_breached(
        self,
        at: datetime,
    ) -> None:
        if self._acknowledgment_sla_breached_at is not None:
            return

        if self._status != AssignmentStatus.PENDING:
            return

        self._acknowledgment_sla_breached_at = at
        self._enable_all_claims()

        self._touch(at)

    def mark_resolution_sla_breached(
        self,
        at: datetime,
    ) -> None:
        if self._resolution_sla_breached_at is not None:
            return

        if self._is_terminal():
            return

        self._resolution_sla_breached_at = at
        self._touch(at)

    def claim(
        self,
        agent_id: str,
        at: datetime,
    ) -> None:

        if self._responsible_agent_id is not None:
            raise AlreadyClaimed(
                "ticket has been already claimed"
            )

        if self._status != AssignmentStatus.PENDING:
            raise NotAvailableToClaim(
                "Only pending assignments can be claimed"
            )

        agent = self._find_agent(agent_id)

        if agent is None:
            raise AgentNotFound(
                "Agent is not a recipient of this assignment"
            )

        agent.claim(at)

        self._responsible_agent_id = agent_id
        self._status = AssignmentStatus.IN_PROGRESS

        self._disable_all_claims()

        self._touch(at)

    def mark_completed(self, at: datetime) -> None:
        if self._status not in {
            AssignmentStatus.IN_PROGRESS,
        }:
            raise AssignmentIncompletable(
                "Only a in-progress assignment can be completed"
            )

        self._status = AssignmentStatus.COMPLETED
        self._completed_at = at

        self._disable_all_claims()
        self._touch(at)

    def mark_cancelled(self, at: datetime) -> None:
        if self._is_terminal():
            raise AssignmentAlreadyTerminated(
                "Terminal assignments cannot be cancelled"
            )

        self._status = AssignmentStatus.CANCELLED

        self._disable_all_claims()
        self._touch(at)

    def mark_superseded(self, at: datetime) -> None:
        if self._is_terminal():
            raise AssignmentAlreadyTerminated(
                "Terminal assignments cannot be superseded"
            )

        self._status = AssignmentStatus.SUPERSEDED

        self._disable_all_claims()
        self._touch(at)

    def can_be_claimed_by(self, agent_id: str) -> bool:

        if self._status != AssignmentStatus.PENDING:
            return False

        if self._responsible_agent_id is not None:
            return False

        for team in self._team_recipients:
            for agent in team.agents:
                if agent.agent_id == agent_id:
                    return (
                        agent.can_claim
                        and agent.claimed_at is None
                    )

        return False
