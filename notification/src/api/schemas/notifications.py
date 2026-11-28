from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    recipient_user_id: str
    event_type: str
    ticket_id: str
    assignment_id: str | None
    title: str
    message: str
    requires_action: bool
    created_at: datetime
    read_at: datetime | None
    is_read: bool


class NotificationListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[NotificationResponse]
    total: int
    page: int
    limit: int


class UnreadCountResponse(BaseModel):
    unread_count: int


class MarkAllReadResponse(BaseModel):
    updated_count: int
