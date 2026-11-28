from sqlalchemy.ext.asyncio import AsyncSession

from src.application.delivery.delivery_service import DeliveryService
from src.application.notification.create_notification import CreateNotification
from src.config.settings import settings
from src.infrastructure.identity.id_generator import IdGenerator
from src.infrastructure.persistence.sqlalchemy.repositories.notification_repository import (
    NotificationRepository,
)
from src.infrastructure.providers.smtp.smtp_email_sender import SmtpEmailSender


def get_create_notification(session: AsyncSession) -> CreateNotification:
    repository = NotificationRepository(session)

    delivery_service = DeliveryService(
        repository=repository,
        email_sender=SmtpEmailSender(settings=settings),
    )

    return CreateNotification(
        repository=repository,
        id_generator=IdGenerator(),
        delivery_service=delivery_service,
    )
