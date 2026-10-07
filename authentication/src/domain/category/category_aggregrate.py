from dataclasses import dataclass
from datetime import datetime

from src.domain.shared.aggregrate import AggregrateRoot

@dataclass
class CategoryAggregrate(AggregrateRoot[str]):

    _name: str
    _description: str
    _is_active: bool = True
    _created_at: datetime | None = None
    _updated_at: datetime | None = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def created_at(self) -> datetime | None:
        return self._created_at

    @property
    def updated_at(self) -> datetime | None:
        return self._updated_at

    @staticmethod
    def create(
        id: str,
        name: str,
        description: str,
    ) -> CategoryAggregrate:

        return CategoryAggregrate(
            _id=id,
            _name=name,
            _description=description,
            _is_active=True,
        )

    def change_name(self, name: str) -> None:
        self._name = name

    def change_description(self, description: str) -> None:
        self._description = description

    def change_activation(self, activation: bool) -> None:
        self._is_active = activation
