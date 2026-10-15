from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector import containers, providers

from ticket.application.shared.date_time_provider_interface import IDateTimeProvider
from ticket.application.shared.id_generator_interface import IIdGenerator
from ticket.application.shared.producer_interface import IProducer
from ticket.infrastructure.persistence.sqlalchemy.unit_of_work import UnitOfWork



class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    session = providers.Dependency(instance_of=AsyncSession)


    id_genertor = providers.Singleton(IIdGenerator)
    datetime_provider = providers.Singleton(IDateTimeProvider)
    producer = providers.Singleton(IProducer)

    unit_of_work = providers.Factory(
        UnitOfWork,
        session=session
    )

container = Container()
