from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column
from analytics.infrastructure.persistence.sqlalchemy.database import Base


class TicketAnalyticsModel(Base):
    __tablename__ = "ticket_analytics"

    ticket_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    category_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    created_by: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    current_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    resolution_duration_seconds: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
