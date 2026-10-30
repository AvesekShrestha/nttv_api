from enum import StrEnum

class TicketActivityType(StrEnum):
    CREATED = "CREATED"
    FORWARDED = "FORWARDED"
    ESCALATED = "ESCALATED "
    TERMINATED = "TERMINATED"

    @classmethod
    def from_string(cls, value: str) -> TicketActivityType:
        return cls(value.strip().upper())
