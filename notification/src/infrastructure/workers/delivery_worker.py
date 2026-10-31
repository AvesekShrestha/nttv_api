import asyncio
import logging

from src.application.delivery.delivery_service import DeliveryService
from src.config.settings import settings
from src.infrastructure.persistence.sqlalchemy.database import SessionLocal
from src.infrastructure.persistence.sqlalchemy.repositories.notification_repository import (
    NotificationRepository,
)
from src.infrastructure.providers.smtp.smtp_email_sender import SmtpEmailSender

logger = logging.getLogger(__name__)


async def process_pending_notifications() -> None:
    async with SessionLocal() as session:
        repository = NotificationRepository(session)

        notification_ids = await repository.get_pending_delivery_ids()

    logger.info(
        "Found %s notifications eligible for delivery",
        len(notification_ids),
    )

    for notification_id in notification_ids:
        try:
            async with SessionLocal() as session:
                repository = NotificationRepository(session)

                delivery_service = DeliveryService(
                    repository=repository,
                    email_sender=SmtpEmailSender(settings=settings),
                )

                await delivery_service.deliver(notification_id)

        except Exception:
            logger.exception(
                "Failed to process notification: %s",
                notification_id,
            )


async def run_worker() -> None:
    logger.info(
        "Delivery worker started. interval=%ss",
        settings.delivery_worker_interval,
    )

    while True:
        try:
            await process_pending_notifications()

        except Exception:
            logger.exception("Delivery worker cycle failed")

        await asyncio.sleep(settings.delivery_worker_interval)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    try:
        asyncio.run(run_worker())

    except KeyboardInterrupt:
        logger.info("Delivery worker stopped")
