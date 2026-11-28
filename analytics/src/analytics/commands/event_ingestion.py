import asyncio
import traceback

from analytics.infrastructure.persistence.sqlalchemy.database import session_factory
from analytics.config.container import container
from analytics.application.shared.exceptions import ApplicationException
from analytics.domain.shared.exceptions import DomainException



async def main() -> None:

    try:
        async with session_factory() as session:

            container.session.override(session)

            try:
                event_ingestion = container.event_ingestion()

                print("Starting event ingestion....")

                await event_ingestion.start()

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
        print("Event Ingestion stopped by user")
