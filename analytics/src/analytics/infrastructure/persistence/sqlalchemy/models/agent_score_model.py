from datetime import datetime

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from analytics.infrastructure.persistence.sqlalchemy.database import Base


class AgentScoreModel(Base):
    __tablename__ = "agent_scores"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    agent_id: Mapped[str] = mapped_column(
        String(50),
        nullable=True
    )

    ticket_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    source_event_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    activity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    points: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

