from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.domain.notification.notification_channel import NotificationChannel
from src.domain.notification.notification_status import NotificationStatus


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    recipient: str
    channel: NotificationChannel
    subject: str
    message: str
    status: NotificationStatus
    created_at: datetime
