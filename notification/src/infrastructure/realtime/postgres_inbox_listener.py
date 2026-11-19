import asyncio
import logging

import asyncpg
from pydantic import ValidationError
from sqlalchemy.engine import make_url

from src.infrastructure.realtime.connection_manager import (
    ConnectionManager,
)
from src.infrastructure.realtime.inbox_signals import (
    InboxSignal,
    SIGNAL_CHANNEL,
)


logger = logging.getLogger(__name__)

RESYNC_MESSAGE = {
    "type": "notifications.changed",
    "reason": "resync",
}


class PostgresInboxListener:
    def __init__(
        self,
        database_url: str,
        manager: ConnectionManager,
    ):
        url = make_url(database_url)

        if url.get_backend_name() != "postgresql":
            raise ValueError(
                "Inbox listener requires PostgreSQL"
            )

        self._dsn = (
            url.set(drivername="postgresql")
            .render_as_string(hide_password=False)
        )

        self._manager = manager
        self._connection: asyncpg.Connection | None = None
        self._disconnected = asyncio.Event()
        self._queue: asyncio.Queue[InboxSignal] = (
            asyncio.Queue(maxsize=1000)
        )
        self._tasks: list[asyncio.Task] = []
        self._resync_needed = False

    async def _connect(self) -> None:
        connection = await asyncpg.connect(
            dsn=self._dsn,
            timeout=10.0,
            command_timeout=10.0,
        )

        try:
            connection.add_termination_listener(
                self._on_terminated
            )

            await connection.add_listener(
                SIGNAL_CHANNEL,
                self._on_notification,
            )

        except BaseException:
            await connection.close(timeout=5.0)
            raise

        self._connection = connection
        logger.info("PostgreSQL inbox listener connected")

    def _on_terminated(
        self,
        connection: asyncpg.Connection,
    ) -> None:
        self._disconnected.set()

    def _on_notification(
        self,
        connection: asyncpg.Connection,
        pid: int,
        channel: str,
        payload: str,
    ) -> None:
        try:
            signal = InboxSignal.model_validate_json(payload)

        except ValidationError:
            logger.warning("Ignored malformed inbox signal")
            return

        try:
            self._queue.put_nowait(signal)

        except asyncio.QueueFull:
            self._resync_needed = True
            logger.warning(
                "Inbox signal queue full; "
                "clients will be asked to resync"
            )

    async def _deliver(self) -> None:
        while True:
            signal = await self._queue.get()

            try:
                if self._resync_needed:
                    self._resync_needed = False

                    await self._manager.broadcast_all(
                        RESYNC_MESSAGE
                    )

                await self._manager.broadcast(
                    signal.user_id,
                    signal.model_dump(
                        exclude={"user_id"},
                        exclude_none=True,
                    ),
                )

            except Exception as exc:
                self._resync_needed = True
                logger.error(
                    "Inbox signal delivery failed: %s",
                    type(exc).__name__,
                )

            finally:
                self._queue.task_done()

    async def _reconnect(self) -> None:
        while True:
            await self._disconnected.wait()

            while True:
                try:
                    if (
                        self._connection is not None
                        and not self._connection.is_closed()
                    ):
                        await self._connection.close(
                            timeout=5.0
                        )

                    self._disconnected.clear()
                    await self._connect()

                    await self._manager.broadcast_all(
                        RESYNC_MESSAGE
                    )
                    break

                except asyncio.CancelledError:
                    raise

                except Exception as exc:
                    logger.warning(
                        "Inbox listener reconnect failed: %s",
                        type(exc).__name__,
                    )
                    await asyncio.sleep(1.0)

    async def start(self) -> None:
        if self._tasks:
            raise RuntimeError(
                "Inbox listener already started"
            )

        self._disconnected.clear()
        await self._connect()

        self._tasks = [
            asyncio.create_task(self._deliver()),
            asyncio.create_task(self._reconnect()),
        ]

    async def stop(self) -> None:
        for task in self._tasks:
            task.cancel()

        await asyncio.gather(
            *self._tasks,
            return_exceptions=True,
        )
        self._tasks.clear()

        if self._connection is not None:
            try:
                await self._connection.close(timeout=5.0)

            finally:
                self._connection = None
