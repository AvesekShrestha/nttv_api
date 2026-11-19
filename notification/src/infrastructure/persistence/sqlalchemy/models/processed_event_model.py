from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.sqlalchemy.base import Base


class ProcessedEventModel(Base):
    __tablename__ = "processed_events"

    source_topic: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
    )

    event_id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
    )

    event_type: Mapped[str] = mapped_column(String(100))

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )

    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
