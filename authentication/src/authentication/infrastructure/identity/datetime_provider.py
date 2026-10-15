from datetime import datetime, timezone

from authentication.application.shared.datetime_provider_interface import IDateTimeProvider

class DateTimeProvider(IDateTimeProvider) : 

    def now(self) -> datetime:
        return datetime.now(timezone.utc)
