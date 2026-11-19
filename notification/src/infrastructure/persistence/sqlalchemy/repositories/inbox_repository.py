from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto.inbox_notification_dto import (
    InboxRecipient,
    RecordTicketEventRequest,
)
from src.application.interfaces.inbox_repository_interface import (
    InboxRepositoryInterface,
)
from src.application.shared.id_generator_interface import IIdGenerator
from src.infrastructure.persistence.sqlalchemy.models.inbox_notification_model import (
    InboxNotificationModel,
)
from src.infrastructure.persistence.sqlalchemy.models.notification_delivery_model import (
    NotificationDeliveryModel,
)
from src.infrastructure.persistence.sqlalchemy.models.processed_event_model import (
    ProcessedEventModel,
)
from src.infrastructure.realtime.inbox_signals import (
    publish_inbox_change,
)


class InboxRepository(InboxRepositoryInterface):
    def __init__(
        self,
        session: AsyncSession,
        id_generator: IIdGenerator,
    ):
        self.session = session
        self.id_generator = id_generator

    async def record_event(
        self,
        request: RecordTicketEventRequest,
    ) -> bool:
        if self.session.in_transaction():
            raise RuntimeError(
                "record_event requires a session without an active transaction"
            )

        if not all(
            value.strip()
            for value in (
                request.source_topic,
                request.event_id,
                request.event_type,
                request.ticket_id,
            )
        ):
            raise ValueError(
                "Topic, event ID, event type, and ticket ID are required"
            )

        if request.occurred_at.utcoffset() is None:
            raise ValueError("occurred_at must include a timezone")

        recipients: dict[str, InboxRecipient] = {}

        for recipient in request.recipients:
            if not all(
                value.strip()
                for value in (
                    recipient.user_id,
                    recipient.title,
                    recipient.message,
                )
            ):
                raise ValueError(
                    "Each recipient needs a user ID, title, and message"
                )

            existing = recipients.get(recipient.user_id)

            if existing is not None and existing != recipient:
                raise ValueError(
                    "Conflicting notification details for user "
                    f"{recipient.user_id}"
                )

            recipients[recipient.user_id] = recipient

        if not recipients:
            raise ValueError(
                "At least one resolved recipient is required"
            )

        async with self.session.begin():
            statement = (
                pg_insert(ProcessedEventModel.__table__)
                .values(
                    source_topic=request.source_topic,
                    event_id=request.event_id,
                    event_type=request.event_type,
                    occurred_at=request.occurred_at,
                )
                .on_conflict_do_nothing(
                    index_elements=["source_topic", "event_id"],
                )
                .returning(ProcessedEventModel.event_id)
            )

            result = await self.session.execute(statement)

            if result.scalar_one_or_none() is None:
                return False

            now = datetime.now(timezone.utc)
            inbox_rows = []
            delivery_rows = []

            for recipient in recipients.values():
                notification_id = (
                    self.id_generator.generate_notification_id()
                )

                inbox_rows.append(
                    {
                        "id": notification_id,
                        "source_topic": request.source_topic,
                        "source_event_id": request.event_id,
                        "recipient_user_id": recipient.user_id,
                        "event_type": request.event_type,
                        "ticket_id": request.ticket_id,
                        "assignment_id": request.assignment_id,
                        "title": recipient.title,
                        "message": recipient.message,
                        "requires_action": recipient.requires_action,
                        "created_at": now,
                    }
                )

                if recipient.send_email:
                    delivery_rows.append(
                        {
                            "id": str(uuid4()),
                            "notification_id": notification_id,
                            "channel": "email",
                            "status": "pending",
                            "attempt_count": 0,
                            "created_at": now,
                        }
                    )

            await self.session.execute(
                insert(InboxNotificationModel.__table__),
                inbox_rows,
            )

            if delivery_rows:
                await self.session.execute(
                    insert(NotificationDeliveryModel.__table__),
                    delivery_rows,
                )

            for row in inbox_rows:
                await publish_inbox_change(
                    self.session,
                    user_id=row["recipient_user_id"],
                    reason="created",
                    notification_id=row["id"],
                )

        return True
