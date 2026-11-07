import asyncio
import traceback

from ticket.application.shared.application_exception import ApplicationException
from ticket.config.container import container
from ticket.domain.shared.domain_exception import DomainException
from ticket.infrastructure.persistence.sqlalchemy.database import session_factory


async def main() -> None:

    try:
        async with session_factory() as session:

            container.session.override(session)

            try:
                dispatcher = container.dispatcher()

                print("Starting Kafka dispatcher...")

                await dispatcher.start()

            finally:
                container.session.reset_override()

    except (ApplicationException, DomainException) as e:
        print(e.message)

    except Exception as exc:
        print(f"Dispatcher failed: {type(exc).__name__}: {exc}")
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Dispatcher stopped by user.")
