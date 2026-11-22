from datetime import timedelta
from typing import Any

from sqlalchemy import and_, case, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto.delivery_job_dto import ClaimedDelivery
from src.application.exceptions.delivery_exception import (
    DeliveryClaimLostError,
)
from src.application.interfaces.delivery_repository_interface import (
    DeliveryRepositoryInterface,
)
from src.infrastructure.persistence.sqlalchemy.models.inbox_notification_model import (
    InboxNotificationModel,
)
from src.infrastructure.persistence.sqlalchemy.models.notification_delivery_model import (
    NotificationDeliveryModel,
)


class DeliveryRepository(DeliveryRepositoryInterface):
    def __init__(
        self,
        session: AsyncSession,
        *,
        max_attempts: int = 3,
        retry_delay_seconds: int = 60,
        lease_seconds: int = 300,
    ) -> None:
        if min(
            max_attempts,
            retry_delay_seconds,
            lease_seconds,
        ) < 1:
            raise ValueError("Delivery policy values must be positive")

        self.session = session
        self.max_attempts = max_attempts
        self.retry_delay_seconds = retry_delay_seconds
        self.lease_seconds = lease_seconds

    def _ensure_ready(self) -> None:
        if self.session.in_transaction():
            raise RuntimeError(
                "Delivery repository requires no active transaction"
            )

    async def claim_next(
        self,
        *,
        delivery_id: str | None = None,
    ) -> ClaimedDelivery | None:
        self._ensure_ready()

        async with self.session.begin():
            now = await self.session.scalar(select(func.now()))

            if now is None:
                raise RuntimeError("Database clock unavailable")

            statement = (
                select(
                    NotificationDeliveryModel,
                    InboxNotificationModel,
                )
                .join(
                    InboxNotificationModel,
                    NotificationDeliveryModel.notification_id
                    == InboxNotificationModel.id,
                )
                .where(
                    NotificationDeliveryModel.channel == "email",
                    NotificationDeliveryModel.attempt_count
                    < self.max_attempts,
                    or_(
                        and_(
                            NotificationDeliveryModel.status
                            == "pending",
                            or_(
                                NotificationDeliveryModel.next_attempt_at.is_(
                                    None
                                ),
                                NotificationDeliveryModel.next_attempt_at
                                <= now,
                            ),
                        ),
                        and_(
                            NotificationDeliveryModel.status
                            == "failed",
                            NotificationDeliveryModel.next_attempt_at.is_not(
                                None
                            ),
                            NotificationDeliveryModel.next_attempt_at
                            <= now,
                        ),
                    ),
                )
                .order_by(
                    NotificationDeliveryModel.created_at,
                    NotificationDeliveryModel.id,
                )
                .limit(1)
                .with_for_update(
                    of=NotificationDeliveryModel,
                    skip_locked=True,
                )
                .execution_options(populate_existing=True)
            )

            if delivery_id is not None:
                statement = statement.where(
                    NotificationDeliveryModel.id == delivery_id
                )

            result = await self.session.execute(statement)
            row = result.first()

            if row is None:
                return None

            delivery, notification = row

            delivery.status = "sending"
            delivery.attempt_count += 1
            delivery.sending_started_at = now
            delivery.next_attempt_at = None
            delivery.last_error = None

            await self.session.flush()

            return ClaimedDelivery(
                id=delivery.id,
                notification_id=notification.id,
                recipient_user_id=notification.recipient_user_id,
                subject=notification.title,
                message=notification.message,
                destination=delivery.destination,
                attempt_count=delivery.attempt_count,
            )

    async def _update_owned(
        self,
        job: ClaimedDelivery,
        **values: Any,
    ) -> None:
        result = await self.session.scalar(
            update(NotificationDeliveryModel)
            .where(
                NotificationDeliveryModel.id == job.id,
                NotificationDeliveryModel.status == "sending",
                NotificationDeliveryModel.attempt_count
                == job.attempt_count,
            )
            .values(**values)
            .returning(NotificationDeliveryModel.id)
        )

        if result is None:
            raise DeliveryClaimLostError(
                "Delivery claim is no longer owned"
            )

    async def set_destination(
        self,
        job: ClaimedDelivery,
        destination: str,
    ) -> None:
        if not destination.strip() or len(destination) > 320:
            raise ValueError("Invalid delivery destination")

        self._ensure_ready()

        async with self.session.begin():
            await self._update_owned(
                job,
                destination=destination,
                sending_started_at=func.now(),
            )

    async def mark_sent(self, job: ClaimedDelivery) -> None:
        self._ensure_ready()

        async with self.session.begin():
            await self._update_owned(
                job,
                status="sent",
                sent_at=func.now(),
                sending_started_at=None,
                next_attempt_at=None,
                last_error=None,
            )

    async def mark_failed(
        self,
        job: ClaimedDelivery,
        *,
        error_code: str,
        permanent: bool = False,
    ) -> None:
        if not error_code.strip():
            raise ValueError("A sanitized error code is required")

        self._ensure_ready()

        async with self.session.begin():
            now = await self.session.scalar(select(func.now()))

            if now is None:
                raise RuntimeError("Database clock unavailable")

            next_attempt_at = None

            if not permanent and job.attempt_count < self.max_attempts:
                delay = min(
                    3600,
                    self.retry_delay_seconds
                    * (2 ** min(job.attempt_count - 1, 10)),
                )
                next_attempt_at = now + timedelta(seconds=delay)

            await self._update_owned(
                job,
                status="failed",
                failed_at=now,
                sending_started_at=None,
                next_attempt_at=next_attempt_at,
                last_error=error_code[:100],
            )

    async def recover_stale_claims(
        self,
        *,
        delivery_id: str | None = None,
    ) -> int:
        self._ensure_ready()
    
        async with self.session.begin():
            now = await self.session.scalar(select(func.now()))
    
            if now is None:
                raise RuntimeError("Database clock unavailable")
    
            statement = (
                update(NotificationDeliveryModel)
                .where(
                    NotificationDeliveryModel.status == "sending",
                    NotificationDeliveryModel.sending_started_at.is_not(
                        None
                    ),
                    NotificationDeliveryModel.sending_started_at
                    <= now - timedelta(seconds=self.lease_seconds),
                )
                .values(
                    status="failed",
                    failed_at=now,
                    sending_started_at=None,
                    last_error="DELIVERY_CLAIM_EXPIRED",
                    next_attempt_at=case(
                        (
                            NotificationDeliveryModel.attempt_count
                            < self.max_attempts,
                            now,
                        ),
                        else_=None,
                    ),
                )
                .returning(NotificationDeliveryModel.id)
            )
    
            if delivery_id is not None:
                statement = statement.where(
                    NotificationDeliveryModel.id == delivery_id
                )
    
            result = await self.session.execute(statement)
            return len(result.scalars().all())
