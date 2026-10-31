import pytest

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from pydantic import BaseModel, ValidationError

from src.infrastructure.messaging.kafka.message_processor import (
    process_message,
)
from src.infrastructure.messaging.kafka.retry_policy import RetryPolicy


def make_message(value=b'{"event_type": "ticket.created"}'):
    message = MagicMock()
    message.topic.return_value = "ticket.events"
    message.partition.return_value = 0
    message.offset.return_value = 10
    message.value.return_value = value
    return message


@pytest.fixture
def consumer():
    instance = MagicMock()
    instance.commit.return_value = [
        SimpleNamespace(error=None)
    ]
    return instance


@pytest.fixture
def producer():
    return MagicMock()


@pytest.fixture
def router():
    instance = MagicMock()
    instance.dispatch = AsyncMock()
    return instance


@pytest.fixture
def retry_policy():
    return RetryPolicy(
        max_attempts=3,
        delay_seconds=0,
    )


@pytest.mark.asyncio
async def test_successful_event_commits(
    consumer,
    producer,
    router,
    retry_policy,
):
    message = make_message()

    await process_message(
        consumer, producer, router, message, retry_policy
    )

    router.dispatch.assert_awaited_once()
    consumer.commit.assert_called_once()


@pytest.mark.asyncio
async def test_invalid_json_goes_to_dlt(
    consumer,
    producer,
    router,
    retry_policy,
):
    message = make_message(b"invalid json")

    with patch(
        "src.infrastructure.messaging.kafka.message_processor.publish_dead_letter",
        new_callable=AsyncMock,
    ) as publish:
        await process_message(
            consumer, producer, router, message, retry_policy
        )

    publish.assert_awaited_once()
    router.dispatch.assert_not_awaited()
    consumer.commit.assert_called_once()


@pytest.mark.asyncio
async def test_invalid_schema_goes_to_dlt(
    consumer,
    producer,
    router,
    retry_policy,
):
    class TestEvent(BaseModel):
        event_id: str

    try:
        TestEvent.model_validate({})
    except ValidationError as exc:
        validation_error = exc

    router.dispatch.side_effect = validation_error
    message = make_message()

    with patch(
        "src.infrastructure.messaging.kafka.message_processor.publish_dead_letter",
        new_callable=AsyncMock,
    ) as publish:
        await process_message(
            consumer, producer, router, message, retry_policy
        )

    publish.assert_awaited_once()
    assert router.dispatch.await_count == 1
    consumer.commit.assert_called_once()


@pytest.mark.asyncio
async def test_retry_then_success(
    consumer,
    producer,
    router,
    retry_policy,
):
    router.dispatch.side_effect = [
        RuntimeError("Temporary error"),
        None,
    ]

    message = make_message()

    with patch(
        "src.infrastructure.messaging.kafka.message_processor.asyncio.sleep",
        new_callable=AsyncMock,
    ):
        await process_message(
            consumer, producer, router, message, retry_policy
        )

    assert router.dispatch.await_count == 2
    consumer.commit.assert_called_once()


@pytest.mark.asyncio
async def test_retries_exhausted_goes_to_dlt(
    consumer,
    producer,
    router,
    retry_policy,
):
    router.dispatch.side_effect = RuntimeError(
        "Database unavailable"
    )

    message = make_message()

    with (
        patch(
            "src.infrastructure.messaging.kafka.message_processor.publish_dead_letter",
            new_callable=AsyncMock,
        ) as publish,
        patch(
            "src.infrastructure.messaging.kafka.message_processor.asyncio.sleep",
            new_callable=AsyncMock,
        ),
    ):
        await process_message(
            consumer, producer, router, message, retry_policy
        )

    assert router.dispatch.await_count == 3
    publish.assert_awaited_once()
    consumer.commit.assert_called_once()


@pytest.mark.asyncio
async def test_dlt_failure_does_not_commit(
    consumer,
    producer,
    router,
    retry_policy,
):
    message = make_message(b"invalid json")

    with patch(
        "src.infrastructure.messaging.kafka.message_processor.publish_dead_letter",
        new_callable=AsyncMock,
        side_effect=RuntimeError("DLT unavailable"),
    ):
        with pytest.raises(RuntimeError, match="DLT unavailable"):
            await process_message(
                consumer, producer, router, message, retry_policy
            )

    consumer.commit.assert_not_called()


@pytest.mark.asyncio
async def test_commit_failure_propagates(
    consumer,
    producer,
    router,
    retry_policy,
):
    consumer.commit.return_value = [
        SimpleNamespace(error="Commit failed")
    ]

    message = make_message()

    with pytest.raises(RuntimeError, match="Kafka commit failed"):
        await process_message(
            consumer, producer, router, message, retry_policy
        )


@pytest.mark.asyncio
async def test_missing_kafka_metadata(
    consumer,
    producer,
    router,
    retry_policy,
):
    message = make_message()
    message.topic.return_value = None

    with pytest.raises(RuntimeError, match="missing topic"):
        await process_message(
            consumer, producer, router, message, retry_policy
        )

    router.dispatch.assert_not_awaited()
    consumer.commit.assert_not_called()
