from sqlalchemy.ext.asyncio import AsyncSession

from application.shared.unit_of_work_interface import IUnitOfWork


class UnitOfWork(IUnitOfWork):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self) -> None:
        print(f"Id from unit of work : {id(self.session)}")
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
