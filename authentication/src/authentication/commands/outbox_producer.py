import asyncio
import logging
from fastapi import Depends

from authentication.config.container import container
from authentication.infrastructure.persistence.sqlalchemy.database import session_factory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:

    async with session_factory() as session:
        container.session.override(session)

        worker = container.outbox_worker()

        try:
            await worker.publish()
        finally:
            worker.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Outbox worker interrupted")
