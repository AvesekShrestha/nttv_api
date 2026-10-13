from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.sqlalchemy.database import Base


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

    assignment: Mapped["Assignment"] = relationship(
        back_populates="team_recipients",
    )
