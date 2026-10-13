from datetime import datetime, timezone

from src.application.shared.date_time_provider_interface import IDateTimeProvider

class DateTimeProvider(IDateTimeProvider) : 

    def now(self) -> datetime:
        return datetime.now(timezone.utc)
