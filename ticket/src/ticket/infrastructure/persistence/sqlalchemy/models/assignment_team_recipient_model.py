from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ticket.infrastructure.persistence.sqlalchemy.database import Base
from ticket.infrastructure.persistence.sqlalchemy.models.assignment_agent_recipient_model import AssignmentAgentRecipient


class AssignmentTeamRecipient(Base):
    __tablename__ = "assignment_team_recipients"

    id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )

    assignment_id: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("assignments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    team_id: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    agent_recipients: Mapped[list["AssignmentAgentRecipient"]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
    ) 
