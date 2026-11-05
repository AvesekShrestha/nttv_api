from ticket.domain.rotation.round_robin_scope import RoundRobinScope
from ticket.infrastructure.persistence.sqlalchemy.models.round_robin_model import (
    RoundRobinModel,
)
from ticket.domain.rotation.round_robin_aggregate import RoundRobinAggregate


class RoundRobinMapper:

    @staticmethod
    def to_domain(model: RoundRobinModel) -> RoundRobinAggregate:
        return RoundRobinAggregate(
            _id=model.id,
            _scope_type=RoundRobinScope.from_string(model.scope_type),
            _scope_id=model.scope_id,
            _last_selected_id=model.last_selected_id,
        )

    @staticmethod
    def to_model(aggregate: RoundRobinAggregate) -> RoundRobinModel:
        return RoundRobinModel(
            id=aggregate.id,
            scope_type=aggregate.scope_type.value,
            scope_id=aggregate.scope_id,
            last_selected_id=aggregate.last_selected_id,
        )
