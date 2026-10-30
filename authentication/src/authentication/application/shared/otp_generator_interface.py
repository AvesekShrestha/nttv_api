from abc import ABC, abstractmethod


class IOTPGenerator(ABC) : 
    @abstractmethod
    def generate(self) -> str : 
        pass
