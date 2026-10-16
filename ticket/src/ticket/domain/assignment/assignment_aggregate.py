from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy import DateTime

from ticket.domain.shared.aggregate import AggregrateRoot
from ticket.domain.assignment.assignment_type import AssignmentType
from ticket.domain.assignment.assignment_status import AssignmentStatus
from ticket.domain.assignment.entity.team_recipient_entity import TeamRecipientEntity


@dataclass
class AssignmentAggregate(AggregrateRoot[str]):
    _ticket_id: str
    _assigned_by: str
    _assignment_type: AssignmentType

    _status: AssignmentStatus = AssignmentStatus.PENDING
    _primary_agent_id: str | None = None
    _responsible_agent_id: str | None = None

    _team_recipients: list[TeamRecipientEntity] = field(default_factory=list)

    _assigned_at: datetime | None = None
    _acknowledgment_deadline_at: datetime | None = None
    _resolution_deadline_at: datetime | None = None

    _acknowledgment_sla_breached_at: datetime | None = None
    _resolution_sla_breached_at: datetime | None = None

    _started_at: datetime | None = None
    _acknowledged_at : datetime | None = None
    _completed_at: datetime | None = None
    _created_at: datetime | None = None
    _updated_at: datetime | None = None

    @property
    def ticket_id(self) -> str:
        return self._ticket_id

    @property
    def assigned_by(self) -> str:
        return self._assigned_by

    @property
    def assignment_type(self) -> AssignmentType:
        return self._assignment_type

    @property
    def assigned_at(self) -> datetime | None:
        return self._assigned_at

    @property
    def started_at(self) -> datetime | None:
        return self._started_at

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
        assigned_by: str,
        assignment_type: AssignmentType,
        assigned_at: datetime,
        acknowledgment_deadline_at: datetime | None = None,
        resolution_deadline_at: datetime | None = None,
        primary_agent_id: str | None = None,
    ) -> AssignmentAggregate:
        if (
            assignment_type == AssignmentType.INITIAL
            and primary_agent_id is None
        ):
            raise ValueError(
                "Initial assignment requires a primary agent"
            )

        if (
            assignment_type != AssignmentType.INITIAL
            and primary_agent_id is not None
        ):
            raise ValueError(
                "Forwarding and escalation must not have a primary agent"
            )

        return AssignmentAggregate(
            _id=id,
            _ticket_id=ticket_id,
            _assigned_by=assigned_by,
            _assignment_type=assignment_type,
            _primary_agent_id=primary_agent_id,
            _responsible_agent_id=primary_agent_id,
            _assigned_at=assigned_at,
            _acknowledgment_deadline_at=acknowledgment_deadline_at,
            _resolution_deadline_at=resolution_deadline_at,
            _created_at=assigned_at,
            _updated_at=assigned_at,
        )

    def add_team_recipient(self, recipients: list[TeamRecipientEntity]) -> None:
        if self._status != AssignmentStatus.PENDING:
            raise ValueError(
                "Recipients can only be added to a pending assignment"
            )

        for recipient in recipients:
            if any(
                existing.team_id == recipient.team_id
                for existing in self._team_recipients
            ):
                raise ValueError("Team already added to this assignment")

            self._team_recipients.append(recipient)

    def mark_acknowledgment_sla_breached(
        self,
        at: datetime,
    ) -> None:
        if self._acknowledgment_sla_breached_at is not None:
            return

        if self._status in {
            AssignmentStatus.COMPLETED,
            AssignmentStatus.CANCELLED,
            AssignmentStatus.SUPERSEDED,
        }:
            return

        self._acknowledgment_sla_breached_at = at

        if self._assignment_type == AssignmentType.INITIAL:
            for team in self._team_recipients:
                for agent in team.agents:
                    if agent.agent_id != self._primary_agent_id:
                        agent.enable_claiming()

        self._updated_at = at

    def mark_resolution_sla_breached(
        self,
        at: datetime,
    ) -> None:
        if self._resolution_sla_breached_at is not None:
            return

        if self._status in {
            AssignmentStatus.COMPLETED,
            AssignmentStatus.CANCELLED,
            AssignmentStatus.SUPERSEDED,
        }:
            return

        self._resolution_sla_breached_at = at
        self._updated_at = at

    def claim(self, agent_id: str, at: datetime) -> None:
        if self._status not in {
            AssignmentStatus.PENDING,
            AssignmentStatus.CLAIMED,
        }:
            raise ValueError("Assignment cannot be claimed in this status")

        if self._responsible_agent_id is not None:
            raise ValueError("Assignment already has a responsible agent")

        recipient = next(
            (
                agent
                for team in self._team_recipients
                if (agent := team.get_agent(agent_id)) is not None
            ),
            None,
        )

        if recipient is None:
            raise ValueError(
                "Agent is not a recipient of this assignment"
            )

        recipient.claim(at)

        self._responsible_agent_id = agent_id
        self._status = AssignmentStatus.CLAIMED

        # A successful claim makes all other recipients ineligible.
        for team in self._team_recipients:
            for agent in team.agents:
                if agent.agent_id != agent_id:
                    agent.disable_claiming()

        self._updated_at = at

    def mark_started(self, at: datetime) -> None:
        if self._status != AssignmentStatus.CLAIMED:
            raise ValueError(
                "Only a claimed assignment can be started"
            )

        self._status = AssignmentStatus.IN_PROGRESS
        self._started_at = at
        self._updated_at = at

    def mark_completed(self, at: datetime) -> None:
        if self._status not in {
            AssignmentStatus.CLAIMED,
            AssignmentStatus.IN_PROGRESS,
        }:
            raise ValueError(
                "Only a claimed or in-progress assignment can be completed"
            )

        self._status = AssignmentStatus.COMPLETED
        self._completed_at = at

        for team in self._team_recipients:
            for agent in team.agents:
                agent.disable_claiming()

        self._updated_at = at

    def mark_cancelled(self, at: datetime) -> None:
        if self._status in {
            AssignmentStatus.COMPLETED,
            AssignmentStatus.SUPERSEDED,
        }:
            raise ValueError(
                "Completed or superseded assignments cannot be cancelled"
            )

        self._status = AssignmentStatus.CANCELLED

        for team in self._team_recipients:
            for agent in team.agents:
                agent.disable_claiming()

        self._updated_at = at

    def mark_superseded(self, at: datetime) -> None:
        if self._status == AssignmentStatus.COMPLETED:
            raise ValueError(
                "Completed assignments cannot be superseded"
            )

        self._status = AssignmentStatus.SUPERSEDED

        for team in self._team_recipients:
            for agent in team.agents:
                agent.disable_claiming()

        self._updated_at = at

    def acknowledge(self, at : datetime)-> None :
        if self._status == AssignmentStatus.COMPLETED:
            raise ValueError(
                "Completed assignments cannot be superseded"
            )

        for team in self._team_recipients:
            for agent in team.agents : 
                agent.disable_claiming()

        self._status = AssignmentStatus.ACKNOWLEDGED
        self._acknowledged_at = at
        self._updated_at = at

