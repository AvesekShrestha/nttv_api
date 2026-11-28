from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    String,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column
from analytics.infrastructure.persistence.sqlalchemy.database import Base



class TicketActivityModel(Base):
    __tablename__ = "ticket_activities"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    source_event_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True
    )

    ticket_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    assignment_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    actor_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    agent_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    team_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    activity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
