from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.inbox_access_repository_interface import (
    InboxAccessRepositoryInterface,
)
from src.infrastructure.persistence.sqlalchemy.database import get_db
from src.infrastructure.persistence.sqlalchemy.repositories.inbox_access_repository import (
    InboxAccessRepository,
)


def get_inbox_access_repository(
    session: AsyncSession = Depends(get_db),
) -> InboxAccessRepositoryInterface:
    return InboxAccessRepository(session)
