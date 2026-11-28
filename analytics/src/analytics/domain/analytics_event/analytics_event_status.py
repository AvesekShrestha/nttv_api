from enum import StrEnum


class AnalyticsEventStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    FAILED = "FAILED"
    PROCESSED = "PROCESSED"
    DEAD_LETTER = "DEAD_LETTER"

    @classmethod
    def from_string(cls, value: str) -> "AnalyticsEventStatus":
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(
                f"Invalid analytics event status: {value}"
            ) from None
