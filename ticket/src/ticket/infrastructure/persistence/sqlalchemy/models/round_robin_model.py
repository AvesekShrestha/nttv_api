from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ticket.infrastructure.persistence.sqlalchemy.database import Base

class RoundRobinModel(Base):

    __tablename__ = "rotation_states"

    __table_args__ = (
        UniqueConstraint(
            "scope_type",
            "scope_id",
            name="uq_rotation_scope",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )

    scope_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    scope_id: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    last_selected_id: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )
