from datetime import date

from pydantic import BaseModel, ConfigDict, model_validator


class TicketAnalyticsQueryDTO(BaseModel):

    model_config = ConfigDict(frozen=True)

    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_date_range(self):

        if self.start_date is None and self.end_date is None:
            return self

        if self.start_date is None or self.end_date is None:
            raise ValueError(
                "Both start_date and end_date must be provided together"
            )

        if self.start_date > self.end_date:
            raise ValueError(
                "start_date cannot be greater than end_date"
            )

        return self
