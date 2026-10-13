from dataclasses import dataclass
from src.domain.shared.entity import Entity

@dataclass
class AggregrateRoot[Id](Entity[Id]):
    pass
