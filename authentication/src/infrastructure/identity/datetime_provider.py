from datetime import datetime

from src.application.shared.datetime_provider_interface import IDateTimeProvider

class DateTimeProvider(IDateTimeProvider) : 

    def now(self) -> datetime:
        return datetime.now()
