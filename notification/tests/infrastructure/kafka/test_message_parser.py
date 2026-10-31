import pytest

from unittest.mock import MagicMock

from src.infrastructure.messaging.kafka.message_parser import (
    InvalidMessageError,
    parse_message,
)


def make_message(value: bytes | None):
    message = MagicMock()
    message.value.return_value = value
    return message


def test_parse_valid_json():
    message = make_message(
        b'{"event_id": "evt-001", "event_type": "ticket.created"}'
    )

    result = parse_message(message)

    assert result["event_id"] == "evt-001"
    assert result["event_type"] == "ticket.created"


def test_parse_empty_message():
    message = make_message(None)

    with pytest.raises(InvalidMessageError):
        parse_message(message)


def test_parse_invalid_json():
    message = make_message(b'{"event_id":')

    with pytest.raises(InvalidMessageError):
        parse_message(message)


def test_parse_non_object_json():
    message = make_message(b'["event1", "event2"]')

    with pytest.raises(InvalidMessageError):
        parse_message(message)


def test_parse_invalid_utf8():
    message = make_message(b"\xff\xfe")

    with pytest.raises(InvalidMessageError):
        parse_message(message)


def test_parse_empty_json_object():
    message = make_message(b"{}")

    result = parse_message(message)

    assert result == {}
