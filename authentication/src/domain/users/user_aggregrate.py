from dataclasses import dataclass
from datetime import datetime

from src.domain.shared.aggregrate import AggregrateRoot
from src.domain.shared.level import Level
from src.domain.users.user_role import UserRole

@dataclass
class UserAggregrate(AggregrateRoot[str]):

    _username: str
    _email: str
    _password: str
    _level: Level | None = None
    _role: UserRole = UserRole.CUSTOMER
    _is_active: bool = True
    _created_at: datetime | None = None
    _updated_at: datetime | None = None

    @property
    def username(self) -> str:
        return self._username

    @property
    def email(self) -> str:
        return self._email

    @property
    def password(self) -> str:
        return self._password

    @property
    def role(self) -> UserRole:
        return self._role

    @property
    def level(self) -> Level | None:
        return self._level

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
        username: str,
        email: str,
        password: str,
        role: UserRole = UserRole.CUSTOMER,
        level: Level | None = None,
    ) -> UserAggregrate:

        return UserAggregrate(
            _id=id,
            _username=username,
            _email=email,
            _password=password,
            _role=role,
            _level=level,
            _is_active=True,
        )

    def change_username(self, username: str) -> None:
        self._username = username

    def change_email(self, email: str) -> None:
        self._email = email

    def change_password(self, password: str) -> None:
        self._password = password

    def change_role(self, role: UserRole) -> None:
        self._role = role

    def change_level(self, level: Level | None) -> None:
        self._level = level

    def change_activation(self, activation: bool) -> None:
        self._is_active = activation
