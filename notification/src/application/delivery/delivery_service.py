import logging

from src.application.delivery.delivery_service_interface import (
    DeliveryServiceInterface,
)
from src.application.exceptions.delivery_exception import DeliveryError
from src.application.interfaces.notification_repository_interface import (
    NotificationRepositoryInterface,
)
from src.application.shared.email_sender_interface import EmailSenderInterface
from src.domain.notification.notification_channel import NotificationChannel

logger = logging.getLogger(__name__)


class DeliveryService(DeliveryServiceInterface):
    def __init__(
        self,
        repository: NotificationRepositoryInterface,
        email_sender: EmailSenderInterface,
    ) -> None:
        self._repository = repository
        self._email_sender = email_sender

    async def deliver(self, notification_id: str) -> None:
        logger.info("Delivery requested for notification_id=%s", notification_id)

        notification = await self._repository.get_by_id(notification_id)

        if notification is None:
            logger.warning("Notification not found: %s", notification_id)
            return

        if notification.channel != NotificationChannel.EMAIL:
            logger.warning(
                "Skipping notification %s: channel=%s",
                notification_id,
                notification.channel,
            )
            return

        notification.mark_as_sending()
        await self._repository.save(notification)

        try:
            logger.info(
                "Calling email sender for notification_id=%s",
                notification_id,
            )

            await self._email_sender.send(
                notification.recipient,
                notification.subject,
                notification.message,
            )

            notification.mark_as_sent()
            logger.info(
                "Email sender succeeded for notification_id=%s",
                notification_id,
            )

        except DeliveryError as exc:
            logger.exception(
                "Email delivery failed for notification_id=%s",
                notification_id,
            )
            notification.mark_as_failed(str(exc))

        except Exception:
            logger.exception(
                "Unexpected error during delivery for notification_id=%s",
                notification_id,
            )
            raise

        await self._repository.save(notification)
        logger.info("Final notification state saved: %s", notification_id)
