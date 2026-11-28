from enum import StrEnum


class TicketActivityType(StrEnum):
    DISPATCHED = "DISPATCHED"
    ASSIGNED = "ASSIGNED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    FORWARDED = "FORWARDED"
    ESCALATED = "ESCALATED"
    COMPLETED = "COMPLETED"
    SLA_BREACHED = "SLA_BREACHED"

    @classmethod
    def from_string(cls, value: str) -> TicketActivityType:
        return cls(value.strip().upper())
