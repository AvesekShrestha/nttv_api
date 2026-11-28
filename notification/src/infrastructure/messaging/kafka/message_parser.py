import json
from typing import Any

from confluent_kafka import Message


class InvalidMessageError(ValueError):
    pass


def parse_message(message: Message) -> dict[str, Any]:
    value = message.value()

    if value is None:
        raise InvalidMessageError("Kafka message is empty")

    try:
        payload = json.loads(value)

    except (json.JSONDecodeError, UnicodeDecodeError):
        raise InvalidMessageError(
            "Kafka message contains invalid JSON"
        ) from None

    if not isinstance(payload, dict):
        raise InvalidMessageError(
            "Kafka event must be a JSON object"
        )

    return payload
