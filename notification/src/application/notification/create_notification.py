from src.application.delivery.delivery_service_interface import (
    DeliveryServiceInterface,
)
from src.application.dto.create_notification_dto import CreateNotificationRequest
from src.application.interfaces.notification_repository_interface import (
    NotificationRepositoryInterface,
)
from src.application.shared.id_generator_interface import IIdGenerator
from src.domain.notification.notification_aggregate import NotificationAggregrate


class CreateNotification:
    def __init__(
        self,
        repository: NotificationRepositoryInterface,
        id_generator: IIdGenerator,
        delivery_service: DeliveryServiceInterface,
    ):
        self.repository = repository
        self.id_generator = id_generator
        self.delivery_service = delivery_service

    async def execute(
        self,
        dto: CreateNotificationRequest,
        *,
        source_event_id: str | None = None,
    ) -> NotificationAggregrate | None:
        notification = NotificationAggregrate.create(
            id=self.id_generator.generate_notification_id(),
            recipient=dto.recipient,
            channel=dto.channel,
            subject=dto.subject,
            message=dto.message,
        )

        saved = await self.repository.save(
            notification,
            source_event_id=source_event_id,
        )

        if not saved:
            return None

        await self.delivery_service.deliver(notification.id)

        # Reload to return the latest persisted status.
        return await self.repository.get_by_id(notification.id)
