from dataclasses import dataclass
from typing import Generic, TypeVar


@dataclass
class PaginatedResponse[T]:
    items: list[T]
    total: int
    page: int
    limit: int

    @property
    def total_pages(self) -> int:
        return (self.total + self.limit - 1) // self.limit
