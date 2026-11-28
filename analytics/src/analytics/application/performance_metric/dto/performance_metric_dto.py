from pydantic import BaseModel, ConfigDict


class PerformanceMetricQueryDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    dimension_type: str
    dimension_id: str


class PerformanceMetricResponseDTO(BaseModel):
    id: str
    dimension_type: str
    dimension_id: str

    # Ticket counters
    tickets_received: int
    tickets_acknowledged: int
    tickets_resolved: int
    tickets_forwarded: int
    tickets_escalated: int

    # Acknowledgment SLA
    acknowledgment_sla_eligible: int
    acknowledgment_sla_breached: int

    # Resolution SLA
    resolution_sla_eligible: int
    resolution_sla_breached: int

    # Duration metrics
    total_acknowledgment_seconds: int
    total_resolution_seconds: int


class PerformanceMetricSummaryResponseDTO(BaseModel):
    dimension_type: str
    dimension_id: str

    # Ticket counters
    total_tickets_received: int
    total_tickets_acknowledged: int
    total_tickets_resolved: int
    total_tickets_forwarded: int
    total_tickets_escalated: int

    # Acknowledgment SLA
    total_acknowledgment_sla_eligible: int
    total_acknowledgment_sla_breached: int

    # Resolution SLA
    total_resolution_sla_eligible: int
    total_resolution_sla_breached: int

    # Average durations
    avg_acknowledgment_seconds: float
    avg_resolution_seconds: float
