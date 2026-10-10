from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.notification_repository_interface import (
    NotificationRepositoryInterface,
)
from src.application.notification.create_notification import CreateNotification
from src.application.notification.get_notification import GetNotification
from src.application.shared.id_generator_interface import IIdGenerator
from src.infrastructure.identity.id_generator import IdGenerator
from src.infrastructure.persistence.sqlalchemy.database import (
    get_db,
)
from src.infrastructure.persistence.sqlalchemy.repositories.notification_repository import (
    SQLAlchemyNotificationRepository,
)

from src.config.settings import settings
from src.application.delivery.delivery_service import DeliveryService
from src.application.delivery.delivery_service_interface import DeliveryServiceInterface
from src.application.shared.email_sender_interface import EmailSenderInterface
from src.infrastructure.providers.smtp.smtp_email_sender import SmtpEmailSender

async def get_notification_repository(
    session: AsyncSession = Depends(get_db),
) -> NotificationRepositoryInterface:
    return SQLAlchemyNotificationRepository(session)


def get_id_generator() -> IIdGenerator:
    return IdGenerator()

def get_email_sender() -> EmailSenderInterface:
    return SmtpEmailSender(settings)

def get_delivery_service(
    repository: NotificationRepositoryInterface = Depends(
        get_notification_repository
    ),
    email_sender: EmailSenderInterface = Depends(get_email_sender),
) -> DeliveryServiceInterface:
    return DeliveryService(repository=repository, email_sender=email_sender)

def get_create_notification_use_case(
    repository: NotificationRepositoryInterface = Depends(
        get_notification_repository
    ),
    id_generator: IIdGenerator = Depends(get_id_generator),
    delivery_service: DeliveryServiceInterface = Depends(
        get_delivery_service
    ),
) -> CreateNotification:
    return CreateNotification(
        repository=repository,
        id_generator=id_generator,
        delivery_service=delivery_service,
    )


def get_get_notification_use_case(
    repository: NotificationRepositoryInterface = Depends(
        get_notification_repository
    ),
) -> GetNotification:
    return GetNotification(repository=repository)




