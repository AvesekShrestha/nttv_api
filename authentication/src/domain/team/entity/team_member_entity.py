from dataclasses import dataclass
from datetime import datetime

from src.domain.shared.entity import Entity

@dataclass
class TeamMember(Entity[str]):

    _user_id: str
    _joined_at: datetime | None = None
    _is_active: bool = True

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def joined_at(self) -> datetime | None:
        return self._joined_at

    @property
    def is_active(self) -> bool:
        return self._is_active

    def change_activation(self, activation: bool) -> None:
        self._is_active = activation
