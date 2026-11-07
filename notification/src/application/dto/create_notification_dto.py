from dataclasses import dataclass

from src.domain.notification.notification_channel import NotificationChannel


@dataclass
class CreateNotificationRequest:
    recipient: str
    channel: NotificationChannel
    subject: str
    message: str
