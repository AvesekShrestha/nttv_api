from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "ADMIN"
    SUPERVISOR = "SUPERVISOR"
    AGENT = "AGENT"
    STAFF = "STAFF"
    CUSTOMER = "CUSTOMER"

    @classmethod
    def from_string(cls, value: str) -> UserRole:
        return cls(value.strip().upper())
