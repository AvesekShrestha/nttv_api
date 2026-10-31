import pytest

from src.infrastructure.messaging.kafka.retry_policy import RetryPolicy


def test_retry_policy_allows_retries():
    policy = RetryPolicy(
        max_attempts=3,
        delay_seconds=5,
    )

    assert policy.should_retry(1) is True
    assert policy.should_retry(2) is True


def test_retry_policy_stops_at_limit():
    policy = RetryPolicy(
        max_attempts=3,
        delay_seconds=5,
    )

    assert policy.should_retry(3) is False


def test_invalid_max_attempts():
    with pytest.raises(ValueError):
        RetryPolicy(
            max_attempts=0,
            delay_seconds=5,
        )


def test_negative_retry_delay():
    with pytest.raises(ValueError):
        RetryPolicy(
            max_attempts=3,
            delay_seconds=-1,
        )


def test_zero_retry_delay_is_allowed():
    policy = RetryPolicy(
        max_attempts=3,
        delay_seconds=0,
    )

    assert policy.delay_seconds == 0
