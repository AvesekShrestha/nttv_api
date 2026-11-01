from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.sqlalchemy.base import Base


class AuthDeliveryReceiptModel(Base):
    __tablename__ = "auth_delivery_receipts"

    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'SENT')",
            name="ck_auth_delivery_receipts_status",
        ),
    )

    event_id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
