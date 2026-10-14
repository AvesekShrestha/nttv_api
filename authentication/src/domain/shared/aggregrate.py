from dataclasses import dataclass

from domain.shared.entity import Entity

@dataclass
class AggregrateRoot[Id](Entity[Id]):
    pass
