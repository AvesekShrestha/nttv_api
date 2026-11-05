from enum import StrEnum

class RoundRobinScope(StrEnum):
    TEAM = "TEAM"
    AGENT = "AGENT"

    @classmethod
    def from_string(cls, value: str) -> RoundRobinScope:
        return cls(value.strip().upper())
