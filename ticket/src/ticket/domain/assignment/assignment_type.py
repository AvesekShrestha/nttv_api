from enum import StrEnum

class AssignmentType(StrEnum):
    SYSTEM = "SYSTEM"
    FORWARD = "FORWARD"
    ESCALATION = "ESCALATION"

    @classmethod
    def from_string(cls, value: str) -> AssignmentType:
        return cls(value.strip().upper())
