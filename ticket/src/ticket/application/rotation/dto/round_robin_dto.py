from pydantic import BaseModel, ConfigDict

from ticket.domain.rotation.round_robin_scope import RoundRobinScope

class RoundRobinCreateDTO(BaseModel):
    id: str
    scope_type: RoundRobinScope
    scope_id: str
    last_selected_id: str | None = None

class RoundRobinUpdateDTO(BaseModel):
    last_selected_id: str | None


class RoundRobinResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    scope_type: RoundRobinScope
    scope_id: str
    last_selected_id: str | None
