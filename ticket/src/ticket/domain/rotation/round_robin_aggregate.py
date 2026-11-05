from dataclasses import dataclass

from ticket.application.assignment.dto.team_data_dto import TeamDetailResponseDTO
from ticket.domain.assignment.exceptions.assignment_exception import IneligibleRecipient
from ticket.domain.shared.aggregate import AggregrateRoot
from ticket.domain.rotation.round_robin_scope import RoundRobinScope


@dataclass
class RoundRobinAggregate(AggregrateRoot[str]):

    _scope_type: RoundRobinScope
    _scope_id: str
    _last_selected_id: str | None = None

    @classmethod
    def create(
        cls,
        id: str,
        scope_type: RoundRobinScope,
        scope_id: str,
    ) -> RoundRobinAggregate:

        return RoundRobinAggregate(
            _id=id,
            _scope_type=scope_type,
            _scope_id=scope_id,
        )

    def select_next(self, candidates: list[str]) -> str:

        if not candidates:
            raise IneligibleRecipient("No eligible candidates available")

        if self._last_selected_id not in candidates:
            selected_id = candidates[0]
        else:
            current_index = candidates.index(self._last_selected_id)
            next_index = (current_index + 1) % len(candidates)

            selected_id = candidates[next_index]

        self._last_selected_id = selected_id

        return selected_id

    @property
    def scope_type(self) -> RoundRobinScope:
        return self._scope_type

    @property
    def scope_id(self) -> str:
        return self._scope_id

    @property
    def last_selected_id(self) -> str | None:
        return self._last_selected_id
