import logging

from src.application.delivery.delivery_service import DeliveryService
from src.application.dto.create_notification_dto import (
    CreateNotificationRequest,
)
from src.application.notification.create_notification import CreateNotification
from src.config.settings import settings
from src.domain.notification.notification_channel import NotificationChannel
from src.infrastructure.identity.id_generator import IdGenerator
from src.infrastructure.persistence.sqlalchemy.database import SessionLocal
from src.infrastructure.persistence.sqlalchemy.repositories.notification_repository import (
    SQLAlchemyNotificationRepository,
)
from src.infrastructure.providers.smtp.smtp_email_sender import SmtpEmailSender

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
        repository = SQLAlchemyNotificationRepository(session)
        email_sender = SmtpEmailSender(settings=settings)

        delivery_service = DeliveryService(
            repository=repository,
            email_sender=email_sender,
        )

        use_case = CreateNotification(
            repository=repository,
            id_generator=IdGenerator(),
            delivery_service=delivery_service,
        )

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
