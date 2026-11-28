from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.authentication import CurrentUser, get_current_user
from src.api.dependencies import get_inbox_access_repository
from src.api.schemas.notifications import (
    MarkAllReadResponse,
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
)
from src.application.interfaces.inbox_access_repository_interface import (
    InboxAccessRepositoryInterface,
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    unread_only: bool = False,
    user: CurrentUser = Depends(get_current_user),
    repository: InboxAccessRepositoryInterface = Depends(
        get_inbox_access_repository
    ),
):
    result = await repository.list_for_user(
        user.id,
        page=page,
        limit=limit,
        unread_only=unread_only,
    )

    return NotificationListResponse.model_validate(result)


@router.get("/unread-count", response_model=UnreadCountResponse)
async def unread_count(
    user: CurrentUser = Depends(get_current_user),
    repository: InboxAccessRepositoryInterface = Depends(
        get_inbox_access_repository
    ),
):
    count = await repository.count_unread(user.id)
    return UnreadCountResponse(unread_count=count)


@router.patch("/read-all", response_model=MarkAllReadResponse)
async def mark_all_read(
    user: CurrentUser = Depends(get_current_user),
    repository: InboxAccessRepositoryInterface = Depends(
        get_inbox_access_repository
    ),
):
    count = await repository.mark_all_read(user.id)
    return MarkAllReadResponse(updated_count=count)


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str,
    user: CurrentUser = Depends(get_current_user),
    repository: InboxAccessRepositoryInterface = Depends(
        get_inbox_access_repository
    ),
):
    item = await repository.get_for_user(
        user.id,
        notification_id,
    )

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    return NotificationResponse.model_validate(item)


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
async def mark_notification_read(
    notification_id: str,
    user: CurrentUser = Depends(get_current_user),
    repository: InboxAccessRepositoryInterface = Depends(
        get_inbox_access_repository
    ),
):
    item = await repository.mark_read(
        user.id,
        notification_id,
    )

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    return NotificationResponse.model_validate(item)
