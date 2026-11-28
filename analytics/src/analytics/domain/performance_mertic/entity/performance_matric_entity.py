from analytics.domain.shared.entity import Entity


class PerformanceMetricEntity(Entity[str]):
    def __init__(
        self,
        metric_id: str,
        dimension_type: str,
        dimension_id: str,
        tickets_received: int = 0,
        tickets_acknowledged: int = 0,
        tickets_resolved: int = 0,
        tickets_forwarded: int = 0,
        tickets_escalated: int = 0,
        acknowledgment_sla_eligible: int = 0,
        acknowledgment_sla_breached: int = 0,
        resolution_sla_eligible: int = 0,
        resolution_sla_breached: int = 0,
        total_acknowledgment_seconds: int = 0,
        total_resolution_seconds: int = 0,
    ):
        super().__init__(metric_id)

        self._dimension_type = dimension_type
        self._dimension_id = dimension_id

        self._tickets_received = tickets_received
        self._tickets_acknowledged = tickets_acknowledged
        self._tickets_resolved = tickets_resolved
        self._tickets_forwarded = tickets_forwarded
        self._tickets_escalated = tickets_escalated

        self._acknowledgment_sla_eligible = acknowledgment_sla_eligible
        self._acknowledgment_sla_breached = acknowledgment_sla_breached

        self._resolution_sla_eligible = resolution_sla_eligible
        self._resolution_sla_breached = resolution_sla_breached

        self._total_acknowledgment_seconds = total_acknowledgment_seconds
        self._total_resolution_seconds = total_resolution_seconds

    @staticmethod
    def create(
        metric_id: str,
        dimension_type: str,
        dimension_id: str,
    ) -> "PerformanceMetricEntity":

        return PerformanceMetricEntity(
            metric_id=metric_id,
            dimension_type=dimension_type,
            dimension_id=dimension_id,
        )

    @property
    def dimension_type(self) -> str:
        return self._dimension_type

    @property
    def dimension_id(self) -> str:
        return self._dimension_id

    @property
    def tickets_received(self) -> int:
        return self._tickets_received

    @property
    def tickets_acknowledged(self) -> int:
        return self._tickets_acknowledged

    @property
    def tickets_resolved(self) -> int:
        return self._tickets_resolved

    @property
    def tickets_forwarded(self) -> int:
        return self._tickets_forwarded

    @property
    def tickets_escalated(self) -> int:
        return self._tickets_escalated

    @property
    def acknowledgment_sla_eligible(self) -> int:
        return self._acknowledgment_sla_eligible

    @property
    def acknowledgment_sla_breached(self) -> int:
        return self._acknowledgment_sla_breached

    @property
    def resolution_sla_eligible(self) -> int:
        return self._resolution_sla_eligible

    @property
    def resolution_sla_breached(self) -> int:
        return self._resolution_sla_breached

    @property
    def total_acknowledgment_seconds(self) -> int:
        return self._total_acknowledgment_seconds

    @property
    def total_resolution_seconds(self) -> int:
        return self._total_resolution_seconds

    def record_ticket_acknowledged(
        self, acknowledgment_seconds: int, sla_breached: bool
    ):
        self._tickets_acknowledged += 1
        self._acknowledgment_sla_eligible += 1
        self._total_acknowledgment_seconds += acknowledgment_seconds

        if sla_breached:
            self._acknowledgment_sla_breached += 1

    def record_ticket_forwarded(self):
        self._tickets_forwarded += 1

    def record_ticket_escalated(self):
        self._tickets_escalated += 1

    def record_acknowledgment_sla_breach(self):
        self._acknowledgment_sla_eligible += 1
        self._acknowledgment_sla_breached += 1

    def record_resolution_sla_breach(self):
        self._resolution_sla_eligible += 1
        self._resolution_sla_breached += 1

    def record_ticket_resolved(
        self,
        resolution_seconds: int,
        sla_breached: bool,
    ) -> None:

        self._tickets_resolved += 1
        self._resolution_sla_eligible += 1
        self._total_resolution_seconds += resolution_seconds

        if sla_breached:
            self._resolution_sla_breached += 1
