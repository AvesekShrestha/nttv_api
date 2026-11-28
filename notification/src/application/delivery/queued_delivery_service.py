import logging

from src.application.exceptions.delivery_exception import (
    DeliveryError,
    PermanentDeliveryError,
)
from src.application.interfaces.delivery_repository_interface import (
    DeliveryRepositoryInterface,
)
from src.application.shared.email_sender_interface import (
    EmailSenderInterface,
)
from src.application.shared.recipient_email_resolver_interface import (
    RecipientEmailResolverInterface,
)

logger = logging.getLogger(__name__)


class QueuedDeliveryService:
    def __init__(
        self,
        repository: DeliveryRepositoryInterface,
        email_resolver: RecipientEmailResolverInterface,
        email_sender: EmailSenderInterface,
    ) -> None:
        self._repository = repository
        self._email_resolver = email_resolver
        self._email_sender = email_sender

    async def deliver_next(
        self,
        *,
        delivery_id: str | None = None,
    ) -> bool:
        """Return False when no eligible job was claimed."""
        job = await self._repository.claim_next(
            delivery_id=delivery_id
        )

        if job is None:
            return False

        stage = "RECIPIENT_LOOKUP"

        try:
            destination = job.destination

            if destination is None:
                destination = await self._email_resolver.get_email(
                    job.recipient_user_id
                )

            # Save the address and renew the claim before sending.
            await self._repository.set_destination(
                job,
                destination,
            )

            stage = "SMTP"

            await self._email_sender.send(
                destination,
                job.subject,
                job.message,
            )

        except PermanentDeliveryError:
            await self._repository.mark_failed(
                job,
                error_code=f"{stage}_PERMANENT",
                permanent=True,
            )

            logger.warning(
                "Delivery permanently failed: delivery_id=%s stage=%s",
                job.id,
                stage,
            )
            return True

        except DeliveryError:
            await self._repository.mark_failed(
                job,
                error_code=f"{stage}_TEMPORARY",
            )

            logger.warning(
                "Delivery failed: delivery_id=%s stage=%s",
                job.id,
                stage,
            )
            return True

        # Keep this outside the sending error handler:
        # a database failure here must not be recorded as SMTP failure.
        await self._repository.mark_sent(job)

        logger.info(
            "Email accepted by SMTP server: delivery_id=%s",
            job.id,
        )
        return True
