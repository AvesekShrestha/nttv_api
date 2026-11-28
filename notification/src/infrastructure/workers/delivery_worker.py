import argparse
import asyncio
import getpass
import logging
from pathlib import Path
import signal
import sys

import httpx

from src.application.delivery.queued_delivery_service import (
    QueuedDeliveryService,
)
from src.application.exceptions.delivery_exception import (
    DeliveryClaimLostError,
)
from src.config.settings import settings
from src.infrastructure.clients.recipient_email_client import (
    RecipientEmailClient,
)
from src.infrastructure.clients.worker_auth_session import (
    WorkerAuthenticationError,
    WorkerAuthSession,
)
from src.infrastructure.persistence.sqlalchemy.database import (
    SessionLocal,
    engine,
)
from src.infrastructure.persistence.sqlalchemy.repositories.delivery_repository import (
    DeliveryRepository,
)
from src.infrastructure.providers.smtp.smtp_email_sender import (
    SmtpEmailSender,
)

logger = logging.getLogger(__name__)


async def process_pending_notifications(
    auth: WorkerAuthSession,
    http_client: httpx.AsyncClient,
    email_sender: SmtpEmailSender,
    stop: asyncio.Event,
    *,
    delivery_id: str | None = None,
) -> int:
    # Verify authentication before touching the queue.
    await auth.refresh()

    # A targeted run must not modify other delivery jobs.
    if delivery_id is None:
        async with SessionLocal() as session:
            recovered = await DeliveryRepository(
                session
            ).recover_stale_claims()

        if recovered:
            logger.warning(
                "Recovered %s abandoned delivery claims",
                recovered,
            )

    processed = 0
    limit = 1 if delivery_id is not None else 50

    for _ in range(limit):
        if stop.is_set():
            break

        # Refresh before claiming so authentication failures
        # do not consume delivery attempts.
        token = await auth.refresh()

        resolver = RecipientEmailClient(
            http_client,
            access_token=token,
        )

        try:
            async with SessionLocal() as session:
                service = QueuedDeliveryService(
                    repository=DeliveryRepository(session),
                    email_resolver=resolver,
                    email_sender=email_sender,
                )

                claimed = await service.deliver_next(
                    delivery_id=delivery_id
                )

        except DeliveryClaimLostError:
            logger.warning(
                "Delivery claim changed; skipping stale attempt"
            )
            continue

        if not claimed:
            break

        processed += 1

    return processed


async def run_worker(args: argparse.Namespace) -> None:
    if settings.delivery_worker_interval <= 0:
        raise ValueError(
            "delivery_worker_interval must be positive"
        )

    async with httpx.AsyncClient(
        base_url=settings.authentication_service_url,
        timeout=settings.authentication_api_timeout_seconds,
        follow_redirects=False,
    ) as client:
        auth = WorkerAuthSession(
            client,
            args.session_file,
        )

        email = None
        password = None

        if not args.session_file.exists():
            email = settings.delivery_worker_email
            password = (
                settings.delivery_worker_password
                .get_secret_value()
            )

            if not email or not password:
                if not sys.stdin.isatty():
                    raise WorkerAuthenticationError(
                        "Set DELIVERY_WORKER_EMAIL and "
                        "DELIVERY_WORKER_PASSWORD for first "
                        "login without a terminal"
                    )

                email = email or input(
                    "Worker account email: "
                ).strip()

                password = password or getpass.getpass(
                    "Worker account password: "
                )

        await auth.start(
            email=email,
            password=password,
        )
        del password

        stop = asyncio.Event()
        loop = asyncio.get_running_loop()
        signals = (signal.SIGINT, signal.SIGTERM)

        try:
            for sig in signals:
                loop.add_signal_handler(sig, stop.set)

            email_sender = SmtpEmailSender(settings)

            logger.info(
                "Delivery worker authenticated and started"
            )

            while not stop.is_set():
                processed = await process_pending_notifications(
                    auth,
                    client,
                    email_sender,
                    stop,
                    delivery_id=args.delivery_id,
                )

                logger.info(
                    "Processed %s delivery jobs this cycle",
                    processed,
                )

                if args.once:
                    break

                try:
                    await asyncio.wait_for(
                        stop.wait(),
                        timeout=settings.delivery_worker_interval,
                    )
                except TimeoutError:
                    pass

        finally:
            for sig in signals:
                loop.remove_signal_handler(sig)

            try:
                await auth.logout()

                logger.info(
                    "Worker logged out; session file removed"
                )

            except Exception:
                logger.warning(
                    "Worker logout failed; session file "
                    "retained for restart"
                )


async def main(args: argparse.Namespace) -> None:
    try:
        await run_worker(args)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Notification email delivery worker"
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Run one batch and exit",
    )

    parser.add_argument(
        "--delivery-id",
        help="Process only this delivery job",
    )

    parser.add_argument(
        "--session-file",
        type=Path,
        default=Path(
            ".runtime/delivery-worker-session.json"
        ),
    )

    args = parser.parse_args()

    if args.delivery_id is not None and not args.once:
        parser.error("--delivery-id requires --once")

    logging.basicConfig(level=logging.INFO)

    try:
        asyncio.run(main(args))

    except KeyboardInterrupt:
        logger.info("Delivery worker stopped")

    except Exception:
        logger.exception(
            "Delivery worker stopped due to an error"
        )
        raise SystemExit(1)
