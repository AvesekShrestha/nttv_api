from dataclasses import dataclass

from ticket.domain.shared.entity import Entity

@dataclass
class AggregrateRoot[Id](Entity[Id]):
    pass
