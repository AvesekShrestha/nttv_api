from enum import StrEnum

class Level(StrEnum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"

    @classmethod
    def from_string(cls, value: str) -> Level:
        return cls(value.strip().upper())
