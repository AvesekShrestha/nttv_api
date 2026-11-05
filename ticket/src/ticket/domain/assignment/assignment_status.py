from enum import StrEnum

class AssignmentStatus(StrEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    SUPERSEDED = "SUPERSEDED"

    @classmethod
    def from_string(cls, value: str) -> AssignmentStatus:
        return cls(value.strip().upper())
