from datetime import datetime

from sqlalchemy import DateTime, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.sqlalchemy.base import Base


class NotificationModel(Base):
    __tablename__ = "notifications"

    __table_args__ = (
        UniqueConstraint(
            "source_event_id",
            "recipient",
            name="uq_notifications_source_event_id",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
    )

    source_event_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    recipient: Mapped[str] = mapped_column(String(255))
    channel: Mapped[str] = mapped_column(String(50))
    subject: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    failed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
