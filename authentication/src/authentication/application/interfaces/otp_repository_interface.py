from abc import ABC, abstractmethod

from authentication.domain.otp.otp_aggregate import OTPAggregate

class IOTPRepository(ABC) : 

    @abstractmethod
    async def get_by_email(self, email : str) -> OTPAggregate | None: pass

    @abstractmethod
    async def add(self, aggregate : OTPAggregate) -> OTPAggregate : 
        pass

    @abstractmethod
    async def update(self, aggregate : OTPAggregate) -> OTPAggregate : 
        pass
