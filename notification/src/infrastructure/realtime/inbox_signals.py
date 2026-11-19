from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


SIGNAL_CHANNEL = "ntc_inbox_changes"
ChangeReason = Literal["created", "read", "read_all"]


class InboxSignal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["notifications.changed"]
    user_id: str = Field(min_length=1, max_length=255)
    reason: ChangeReason
    notification_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )


async def publish_inbox_change(
    session: AsyncSession,
    *,
    user_id: str,
    reason: ChangeReason,
    notification_id: str | None = None,
) -> None:
    if not session.in_transaction():
        raise RuntimeError(
            "Inbox signals require an active database transaction"
        )

    signal = InboxSignal(
        type="notifications.changed",
        user_id=user_id,
        reason=reason,
        notification_id=notification_id,
    )

    await session.execute(
        text("SELECT pg_notify(:channel, :payload)"),
        {
            "channel": SIGNAL_CHANNEL,
            "payload": signal.model_dump_json(),
        },
    )
