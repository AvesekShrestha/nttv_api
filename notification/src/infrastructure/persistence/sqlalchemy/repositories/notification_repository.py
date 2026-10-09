from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.notification_repository_interface import (
    NotificationRepositoryInterface,
)
from src.domain.notification.notification_aggregate import NotificationAggregrate
from src.domain.notification.notification_channel import NotificationChannel
from src.domain.notification.notification_status import NotificationStatus
from src.infrastructure.persistence.sqlalchemy.models.notification_model import (
    NotificationModel,
)


class SQLAlchemyNotificationRepository(NotificationRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session


    async def save(
        self,
        notification: NotificationAggregrate,
        *,
        source_event_id: str | None = None,
    ) -> bool:
        # Check duplicate source events only when creating a new notification.
        existing = await self.session.get(NotificationModel, notification.id)
    
        if existing is None and source_event_id is not None:
            if await self.exists_by_source_event(
                source_event_id,
                notification.recipient,
            ):
                return False
    
        try:
            if existing is None:
                # New notification: INSERT.
                model = NotificationModel(
                    id=notification.id,
                    source_event_id=source_event_id,
                    recipient=notification.recipient,
                    channel=notification.channel.value,
                    subject=notification.subject,
                    message=notification.message,
                    status=notification.status.value,
                    created_at=notification.created_at,
                    sent_at=notification.sent_at,
                    failed_at=notification.failed_at,
                )
                self.session.add(model)
            else:
                # Existing notification: UPDATE.
                existing.recipient = notification.recipient
                existing.channel = notification.channel.value
                existing.subject = notification.subject
                existing.message = notification.message
                existing.status = notification.status.value
                existing.sent_at = notification.sent_at
                existing.failed_at = notification.failed_at
    
            await self.session.commit()
            return True
    
        except IntegrityError:
            await self.session.rollback()
    
            if source_event_id is not None:
                if await self.exists_by_source_event(
                    source_event_id,
                    notification.recipient,
                ):
                    return False
    
            raise

    async def get_by_id(
        self,
        notification_id: str,
    ) -> NotificationAggregrate | None:
        result = await self.session.execute(
            select(NotificationModel).where(
                NotificationModel.id == notification_id
            )
        )

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return NotificationAggregrate(
            _id=model.id,
            _recipient=model.recipient,
            _channel=NotificationChannel(model.channel),
            _subject=model.subject,
            _message=model.message,
            _status=NotificationStatus(model.status),
            _created_at=model.created_at,
            _sent_at=model.sent_at,
            _failed_at=model.failed_at,
        )

    async def exists_by_source_event(
        self,
        source_event_id: str,
        recipient: str,
    ) -> bool:
        result = await self.session.execute(
            select(
                exists().where(
                    NotificationModel.source_event_id == source_event_id,
                    NotificationModel.recipient == recipient,
                )
            )
        )
        return bool(result.scalar()) 
