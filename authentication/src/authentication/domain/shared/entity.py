from dataclasses import dataclass

@dataclass
class Entity[Id]:
    _id : Id

    @property
    def id(self)-> Id:
        return self._id

    def __eq__(self, other : object) -> bool : 
        if not isinstance(other, Entity) : return False
        return other.id == self._id

    def __hash__(self) -> int:
       return hash(self._id)
