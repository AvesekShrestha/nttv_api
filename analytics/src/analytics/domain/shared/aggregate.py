from dataclasses import dataclass

from analytics.domain.shared.entity import Entity

@dataclass
class AggregrateRoot[Id](Entity[Id]):
    pass
