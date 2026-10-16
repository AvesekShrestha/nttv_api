from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ticket.infrastructure.persistence.sqlalchemy.database import Base


class TicketActivity(Base):
    __tablename__ = "ticket_activities"

    id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )

    ticket_id: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    assignment_id: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        default=None,
        index=True,
    )

    activity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    actor_id: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
