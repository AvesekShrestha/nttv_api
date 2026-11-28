from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto.inbox_query_dto import InboxItem, InboxPage
from src.application.interfaces.inbox_access_repository_interface import (
    InboxAccessRepositoryInterface,
)
from src.infrastructure.persistence.sqlalchemy.models.inbox_notification_model import (
    InboxNotificationModel,
)
from src.infrastructure.realtime.inbox_signals import (
    publish_inbox_change,
)


class InboxAccessRepository(InboxAccessRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_item(model: InboxNotificationModel) -> InboxItem:
        return InboxItem(
            id=model.id,
            recipient_user_id=model.recipient_user_id,
            event_type=model.event_type,
            ticket_id=model.ticket_id,
            assignment_id=model.assignment_id,
            title=model.title,
            message=model.message,
            requires_action=model.requires_action,
            created_at=model.created_at,
            read_at=model.read_at,
        )

    async def list_for_user(
        self,
        user_id: str,
        *,
        page: int = 1,
        limit: int = 20,
        unread_only: bool = False,
    ) -> InboxPage:
        if page < 1 or not 1 <= limit <= 100:
            raise ValueError("Invalid pagination")

        filters = [
            InboxNotificationModel.recipient_user_id == user_id,
        ]

        if unread_only:
            filters.append(
                InboxNotificationModel.read_at.is_(None)
            )

        total = await self.session.scalar(
            select(func.count())
            .select_from(InboxNotificationModel)
            .where(*filters)
        )

        result = await self.session.execute(
            select(InboxNotificationModel)
            .where(*filters)
            .order_by(
                InboxNotificationModel.created_at.desc(),
                InboxNotificationModel.id.desc(),
            )
            .offset((page - 1) * limit)
            .limit(limit)
        )

        return InboxPage(
            items=[
                self._to_item(model)
                for model in result.scalars().all()
            ],
            total=int(total or 0),
            page=page,
            limit=limit,
        )

    async def get_for_user(
        self,
        user_id: str,
        notification_id: str,
    ) -> InboxItem | None:
        model = await self.session.scalar(
            select(InboxNotificationModel).where(
                InboxNotificationModel.id == notification_id,
                InboxNotificationModel.recipient_user_id == user_id,
            )
        )

        return self._to_item(model) if model is not None else None

    async def count_unread(self, user_id: str) -> int:
        count = await self.session.scalar(
            select(func.count())
            .select_from(InboxNotificationModel)
            .where(
                InboxNotificationModel.recipient_user_id == user_id,
                InboxNotificationModel.read_at.is_(None),
            )
        )

        return int(count or 0)

    async def mark_read(
        self,
        user_id: str,
        notification_id: str,
    ) -> InboxItem | None:
        async with self.session.begin():
            model = await self.session.scalar(
                update(InboxNotificationModel)
                .where(
                    InboxNotificationModel.id == notification_id,
                    InboxNotificationModel.recipient_user_id == user_id,
                    InboxNotificationModel.read_at.is_(None),
                )
                .values(read_at=func.now())
                .returning(InboxNotificationModel)
            )

            if model is None:
                return await self.get_for_user(
                    user_id,
                    notification_id,
                )

            await publish_inbox_change(
                self.session,
                user_id=user_id,
                reason="read",
                notification_id=notification_id,
            )

            return self._to_item(model)

    async def mark_all_read(self, user_id: str) -> int:
        async with self.session.begin():
            result = await self.session.execute(
                update(InboxNotificationModel)
                .where(
                    InboxNotificationModel.recipient_user_id == user_id,
                    InboxNotificationModel.read_at.is_(None),
                )
                .values(read_at=func.now())
                .returning(InboxNotificationModel.id)
            )

            updated_count = len(result.scalars().all())

            if updated_count:
                await publish_inbox_change(
                    self.session,
                    user_id=user_id,
                    reason="read_all",
                )

            return updated_count
