from abc import ABC, abstractmethod

from src.application.dto.delivery_job_dto import ClaimedDelivery


class DeliveryRepositoryInterface(ABC):
    @abstractmethod
    async def claim_next(
        self,
        *,
        delivery_id: str | None = None,
    ) -> ClaimedDelivery | None:
        pass

    @abstractmethod
    async def set_destination(
        self,
        job: ClaimedDelivery,
        destination: str,
    ) -> None:
        pass

    @abstractmethod
    async def mark_sent(self, job: ClaimedDelivery) -> None:
        pass

    @abstractmethod
    async def mark_failed(
        self,
        job: ClaimedDelivery,
        *,
        error_code: str,
        permanent: bool = False,
    ) -> None:
        pass

    @abstractmethod
    async def recover_stale_claims(
    self,
    *,
    delivery_id: str | None = None,
    ) -> int:
        pass
