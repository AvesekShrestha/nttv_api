from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.sqlalchemy.database import Base


class AssignmentAgentRecipient(Base):
    __tablename__ = "assignment_agent_recipients"

    id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )

    team_recipient_id: Mapped[str] = mapped_column(
        String(30),
        ForeignKey(
            "assignment_team_recipients.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    agent_id: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    can_claim: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    notified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    claimed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
