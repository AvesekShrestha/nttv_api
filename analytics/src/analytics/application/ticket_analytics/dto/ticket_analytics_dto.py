from datetime import date

from pydantic import BaseModel


class TicketSummaryDTO(BaseModel):
    total_tickets: int
    resolved_tickets: int
    unresolved_tickets: int
    resolution_rate: float
    average_resolution_seconds: float


class TicketDistributionDTO(BaseModel):
    by_status: dict[str, int]
    by_priority: dict[str, int]
    by_category: dict[str, int]


class TicketTrendDTO(BaseModel):
    date: date
    created: int
    resolved: int


class TicketComparisonDTO(BaseModel):
    current_period_tickets: int
    previous_period_tickets: int
    growth_percentage: float


class TicketAnalysisResponseDTO(BaseModel):
    start_date: date | None = None
    end_date: date | None = None

    summary: TicketSummaryDTO
    distribution: TicketDistributionDTO
    trends: list[TicketTrendDTO]
    comparison: TicketComparisonDTO
