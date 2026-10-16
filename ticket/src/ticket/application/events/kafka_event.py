from datetime import datetime
from pydantic import BaseModel


class KafkaEvent[T](BaseModel):

    id : str
    key : str
    event_type : str
    occurred_at : datetime
    data : T
    published_at : datetime | None = None

