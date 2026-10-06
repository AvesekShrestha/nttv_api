from abc import ABC, abstractmethod 

class IIdGenerator(ABC):

    @abstractmethod
    def generate_user_id(self) -> str: pass

    @abstractmethod
    def generate_ticket_id(self) -> str: pass

    @abstractmethod
    def generate_team_id(self) -> str: pass
        
    @abstractmethod
    def generate_refresh_token_id(self) -> str: pass

    @abstractmethod
    def generate_random_id(self) -> str: pass
