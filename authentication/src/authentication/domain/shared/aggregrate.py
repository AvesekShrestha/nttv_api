from dataclasses import dataclass

from authentication.domain.shared.entity import Entity

@dataclass
class AggregrateRoot[Id](Entity[Id]):
    pass
