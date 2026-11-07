import asyncio
import logging

from ticket.infrastructure.workers.sla_worker import SLABreachWorker
from ticket.infrastructure.persistence.sqlalchemy.database import session_factory

from ticket.config.container import container


logging.basicConfig(level=logging.INFO)


async def main():

    async with session_factory() as session:

        container.session.override(session)
        worker = container.sla_worker()
        await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
