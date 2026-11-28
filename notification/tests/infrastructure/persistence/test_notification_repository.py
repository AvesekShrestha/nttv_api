import pytest

from unittest.mock import AsyncMock, MagicMock

from src.infrastructure.persistence.sqlalchemy.repositories.notification_repository import (
    NotificationRepository,
)


@pytest.fixture
def session():
    instance = MagicMock()
    instance.execute = AsyncMock()
    instance.commit = AsyncMock()
    return instance


@pytest.mark.asyncio
async def test_claim_notification_success(session):
    result = MagicMock()
    result.scalar_one_or_none.return_value = "NOT-001"
    session.execute.return_value = result

    repository = NotificationRepository(session)

    claimed = await repository.claim_for_delivery("NOT-001")

    assert claimed is True
    session.execute.assert_awaited_once()
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_claim_notification_not_eligible(session):
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result

    repository = NotificationRepository(session)

    claimed = await repository.claim_for_delivery("NOT-001")

    assert claimed is False
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_pending_delivery_ids(session):
    result = MagicMock()
    result.scalars.return_value.all.return_value = [
        "NOT-001",
        "NOT-002",
    ]
    session.execute.return_value = result

    repository = NotificationRepository(session)

    ids = await repository.get_pending_delivery_ids(limit=50)

    assert ids == ["NOT-001", "NOT-002"]
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_pending_delivery_ids_empty(session):
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    session.execute.return_value = result

    repository = NotificationRepository(session)

    ids = await repository.get_pending_delivery_ids()

    assert ids == []
