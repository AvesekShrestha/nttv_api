from enum import StrEnum

class TicketStatus(StrEnum):
    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    INPROCESS = "INPROCESS"
    FORWARDED = "FORWARDED"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
