from dataclasses import dataclass, field
from datetime import datetime

from src.domain.shared.aggregrate import AggregrateRoot
from src.domain.shared.level import Level
from src.domain.team.entity.team_member_entity import TeamMember


@dataclass
class TeamAggregate(AggregrateRoot[str]):

    _name: str
    _description: str
    _level: Level = Level.L1
    _is_active: bool = True
    _category_id: str = ""
    _members: list[TeamMember] = field(default_factory=list)
    _created_at: datetime | None = None
    _updated_at: datetime | None = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def level(self) -> Level:
        return self._level

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def category_id(self) -> str:
        return self._category_id

    @property
    def members(self) -> list[TeamMember]:
        return self._members

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
        category_id: str,
        level: Level = Level.L1,
    ) -> "TeamAggregate":

        return TeamAggregate(
            _id=id,
            _name=name,
            _description=description,
            _category_id=category_id,
            _level=level,
            _is_active=True,
        )

    def change_name(self, name: str) -> None:
        self._name = name

    def change_description(self, description: str) -> None:
        self._description = description

    def change_level(self, level: Level) -> None:
        self._level = level

    def change_category(self, category_id: str) -> None:
        self._category_id = category_id

    def change_activation(self, activation: bool) -> None:
        self._is_active = activation

    def add_member(self, member: TeamMember) -> None:
        if any(existing.id == member.id for existing in self._members):
            return

        self._members.append(member)

    def remove_member(self, member_id: str) -> None:
        self._members = [
            member
            for member in self._members
            if member.id != member_id
        ]

    def activate_member(self, member_id: str) -> None:
        for member in self._members:
            if member.id == member_id:
                member.change_activation(True)
                return

    def deactivate_member(self, member_id: str) -> None:
        for member in self._members:
            if member.id == member_id:
                member.change_activation(False)
                return
