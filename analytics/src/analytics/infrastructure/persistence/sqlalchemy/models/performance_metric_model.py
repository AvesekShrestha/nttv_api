from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from analytics.infrastructure.persistence.sqlalchemy.database import Base


class PerformanceMetricModel(Base):
    __tablename__ = "performance_metrics"

    __table_args__ = (
        UniqueConstraint(
            "dimension_type",
            "dimension_id",
            name="uq_performance_dimension",
        ),
        CheckConstraint(
            "dimension_type IN ('AGENT', 'TEAM')",
            name="ck_performance_dimension_type",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )

    dimension_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    dimension_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Ticket counters
    tickets_received: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    tickets_acknowledged: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    tickets_resolved: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    tickets_forwarded: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    tickets_escalated: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    # Acknowledgment SLA
    acknowledgment_sla_eligible: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    acknowledgment_sla_breached: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    # Resolution SLA
    resolution_sla_eligible: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    resolution_sla_breached: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    total_acknowledgment_seconds: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, server_default="0"
    )

    total_resolution_seconds: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, server_default="0"
    )
