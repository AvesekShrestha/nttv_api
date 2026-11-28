from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.sqlalchemy.base import Base


class NotificationDeliveryModel(Base):
    __tablename__ = "notification_deliveries"

    __table_args__ = (
        UniqueConstraint(
            "notification_id",
            "channel",
            name="uq_delivery_inbox_channel",
        ),
        CheckConstraint(
            "channel = 'email'",
            name="ck_delivery_channel",
        ),
        CheckConstraint(
            "status IN ('pending', 'sending', 'sent', 'failed')",
            name="ck_delivery_status",
        ),
        CheckConstraint(
            "attempt_count >= 0",
            name="ck_delivery_attempt_count",
        ),
        Index(
            "ix_delivery_due",
            "status",
            "next_attempt_at",
            "id",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
    )

    notification_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("inbox_notifications.id"),
    )

    channel: Mapped[str] = mapped_column(
        String(50),
        server_default=text("'email'"),
    )

    destination: Mapped[str | None] = mapped_column(
        String(320),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        server_default=text("'pending'"),
    )

    attempt_count: Mapped[int] = mapped_column(
        Integer,
        server_default=text("0"),
    )

    next_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    sending_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    failed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
