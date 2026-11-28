
import logging

from src.application.dto.create_notification_dto import (
    CreateNotificationRequest,
)
from src.domain.notification.notification_channel import NotificationChannel
from src.infrastructure.messaging.kafka.dependencies import (
    get_create_notification,
)
from src.infrastructure.persistence.sqlalchemy.database import SessionLocal

logger = logging.getLogger(__name__)


async def process_notifications(
    *,
    event_id: str,
    event_type: str,
    recipients: list[str],
    subject: str,
    message: str,
) -> None:
    async with SessionLocal() as session:
        use_case = get_create_notification(session)

        try:
            for recipient in recipients:
                dto = CreateNotificationRequest(
                    recipient=recipient,
                    channel=NotificationChannel.EMAIL,
                    subject=subject,
                    message=message,
                )

                notification = await use_case.execute(
                    dto,
                    source_event_id=event_id,
                )

                if notification is None:
                    logger.info(
                        "Duplicate notification skipped: "
                        "event_id=%s recipient=%s",
                        event_id,
                        recipient,
                    )
                    continue

                logger.info(
                    "Notification persisted: "
                    "notification_id=%s event_id=%s recipient=%s status=%s",
                    notification.id,
                    event_id,
                    recipient,
                    notification.status.value,
                )

        except Exception:
            logger.exception(
                "Notification processing failed: "
                "event_id=%s event_type=%s",
                event_id,
                event_type,
            )
            raise
