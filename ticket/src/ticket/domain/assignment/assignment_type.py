from enum import StrEnum

class AssignmentType(StrEnum):
    INITIAL = "INITIAL"
    FORWARD = "FORWARD"
    ESCALATION = "ESCALATION"

    @classmethod
    def from_string(cls, value: str) -> AssignmentType:
        return cls(value.strip().upper())
