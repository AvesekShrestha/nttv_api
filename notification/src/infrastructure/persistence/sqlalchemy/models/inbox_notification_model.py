from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
    false,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.sqlalchemy.base import Base


class InboxNotificationModel(Base):
    __tablename__ = "inbox_notifications"

    __table_args__ = (
        ForeignKeyConstraint(
            ["source_topic", "source_event_id"],
            ["processed_events.source_topic", "processed_events.event_id"],
            name="fk_inbox_processed_event",
        ),
        UniqueConstraint(
            "source_topic",
            "source_event_id",
            "recipient_user_id",
            name="uq_inbox_event_user",
        ),
        Index(
            "ix_inbox_user_created",
            "recipient_user_id",
            "created_at",
            "id",
        ),
        Index(
            "ix_inbox_user_read",
            "recipient_user_id",
            "read_at",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
    )

    source_topic: Mapped[str] = mapped_column(String(255))

    source_event_id: Mapped[str] = mapped_column(String(255))

    recipient_user_id: Mapped[str] = mapped_column(String(255))

    event_type: Mapped[str] = mapped_column(String(100))

    ticket_id: Mapped[str] = mapped_column(String(255))

    assignment_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(String(255))

    message: Mapped[str] = mapped_column(Text)

    requires_action: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=false(),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    @property
    def is_read(self) -> bool:
        return self.read_at is not None
