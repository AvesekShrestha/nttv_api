from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from ticket.infrastructure.persistence.sqlalchemy.database import Base


class ProcessedEvent(Base):

    __tablename__ = "processed_events"

    event_id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
