import asyncio

from ticket.config.container import container

from ticket.domain.event.entity import processed_event_entity
from ticket.infrastructure.persistence.sqlalchemy.database import session_factory


async def main() -> None:

    async with session_factory() as session : 
        container.session.override(session)

        dispatcher = container.dispatcher()

        await dispatcher.start()

if __name__ == "__main__":
    asyncio.run(main())
