from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from ticket.infrastructure.persistence.sqlalchemy.database import Base

from ticket.domain.ticket.ticket_priority import TicketPriority
from ticket.domain.ticket.ticket_status import TicketStatus


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=TicketPriority.MEDIUM.value,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=TicketStatus.NEW.value,
    )

    current_assignment_id : Mapped[str] = mapped_column(
        String(30),
        ForeignKey("assignments.id"),
        nullable=False,
    )

    category_id: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    created_by: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    resolved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
