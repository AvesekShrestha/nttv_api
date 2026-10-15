from enum import StrEnum

class AssignmentStatus(StrEnum):
    PENDING = "PENDING"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    CLAIMED = "CLAIMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    SUPERSEDED = "SUPERSEDED"

    @classmethod
    def from_string(cls, value: str) -> AssignmentStatus:
        return cls(value.strip().upper())
