import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from src.application.shared.email_sender_interface import (
    EmailSenderInterface,
)
from src.infrastructure.persistence.sqlalchemy.database import (
    SessionLocal,
)
from src.infrastructure.persistence.sqlalchemy.models.auth_delivery_receipt_model import (
    AuthDeliveryReceiptModel,
)

logger = logging.getLogger(__name__)


async def deliver_auth_email(
    *,
    event_id: str,
    event_type: str,
    recipient: str,
    subject: str,
    body: str,
    email_sender: EmailSenderInterface,
) -> None:
    async with SessionLocal() as session:
        async with session.begin():
            # Concurrent inserts for the same event wait for the
            # transaction holding that event ID to finish.
            statement = (
                insert(AuthDeliveryReceiptModel)
                .values(
                    event_id=event_id,
                    event_type=event_type,
                    status="PENDING",
                    created_at=datetime.now(timezone.utc),
                    sent_at=None,
                )
                .on_conflict_do_nothing(
                    index_elements=["event_id"],
                )
            )

            await session.execute(statement)

            # Lock the receipt until sending and saving finish.
            result = await session.execute(
                select(AuthDeliveryReceiptModel)
                .where(
                    AuthDeliveryReceiptModel.event_id == event_id
                )
                .with_for_update()
            )

            receipt = result.scalar_one()

            if receipt.event_type != event_type:
                raise ValueError(
                    "Auth event ID reused for a different event type"
                )

            if receipt.status == "SENT":
                logger.info(
                    "Duplicate auth email skipped: "
                    "event_id=%s event_type=%s",
                    event_id,
                    event_type,
                )
                return

            await email_sender.send(
                to=recipient,
                subject=subject,
                body=body,
            )

            receipt.status = "SENT"
            receipt.sent_at = datetime.now(timezone.utc)

        # The transaction has committed successfully here.
        logger.info(
            "Auth email delivery recorded: "
            "event_id=%s event_type=%s",
            event_id,
            event_type,
        )
