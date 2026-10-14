from abc import ABC, abstractmethod 

class IIdGenerator(ABC):

    @abstractmethod
    def generate_user_id(self) -> str: pass

    @abstractmethod
    def generate_team_member_id(self) -> str: pass

    @abstractmethod
    def generate_team_id(self) -> str: pass
        
    @abstractmethod
    def generate_refresh_token_id(self) -> str: pass

    @abstractmethod
    def generate_category_id(self) -> str: pass

    @abstractmethod
    def generate_event_id(self) -> str: pass

    @abstractmethod
    def generate_random_id(self) -> str: pass
