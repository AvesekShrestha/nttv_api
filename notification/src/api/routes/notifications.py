from fastapi import APIRouter, Depends, status

from src.api.dependencies import get_create_notification_use_case, get_get_notification_use_case 
from src.api.schemas.notifications import NotificationResponse
from src.application.dto.create_notification_dto import CreateNotificationRequest
from src.application.notification.create_notification import CreateNotification
from src.application.notification.get_notification import GetNotification

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=NotificationResponse)
async def create_notification_endpoint(
    request: CreateNotificationRequest,
    use_case: CreateNotification = Depends(get_create_notification_use_case),
):
    return await use_case.execute(request)


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification_endpoint(
    notification_id: str,
    use_case: GetNotification = Depends(get_get_notification_use_case),
):
    return await use_case.execute(notification_id)
