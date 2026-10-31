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
from src.domain.notification.notification_status import NotificationStatus

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
        claimed = await self._repository.claim_for_delivery(notification_id)

        if not claimed:
            logger.info(
                "Notification not eligible for delivery: %s",
                notification_id,
            )
            return

        notification = await self._repository.get_by_id(notification_id)

        if notification is None:
            raise RuntimeError(
                f"Claimed notification not found: {notification_id}"
            )

        if notification.status != NotificationStatus.SENDING:
            raise RuntimeError(
                f"Unexpected notification status: {notification.status}"
            )

        try:
            if notification.channel != NotificationChannel.EMAIL:
                raise DeliveryError(
                    f"Unsupported notification channel: {notification.channel}"
                )

            await self._email_sender.send(
                notification.recipient,
                notification.subject,
                notification.message,
            )

        except DeliveryError as exc:
            notification.mark_as_failed(str(exc))
            await self._repository.save(notification)

            logger.warning(
                "Email delivery failed: notification_id=%s error=%s",
                notification_id,
                exc,
            )
            return

        notification.mark_as_sent()
        await self._repository.save(notification)

        logger.info(
            "Email delivered successfully: notification_id=%s",
            notification_id,
        )
