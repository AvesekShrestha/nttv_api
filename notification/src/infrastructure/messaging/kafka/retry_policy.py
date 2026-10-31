from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int
    delay_seconds: float

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError(
                "max_attempts must be at least 1"
            )

        if self.delay_seconds < 0:
            raise ValueError(
                "delay_seconds cannot be negative"
            )

    def should_retry(self, attempt: int) -> bool:
        return attempt < self.max_attempts
