from datetime import datetime, timezone

from sqlalchemy import DateTime, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from authentication.infrastructure.persistence.sqlalchemy.database import Base


class OTP(Base):
    __tablename__ = "opts"

    id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(
        String(254),
        index=True,
        nullable=False,
    )

    otp_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    attempts: Mapped[int] = mapped_column(
        SmallInteger,
        default=0,
        nullable=False,
    )

    max_attempts: Mapped[int] = mapped_column(
        SmallInteger,
        default=3,
        nullable=False,
    )

    consumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    last_sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        nullable=True,
    )
