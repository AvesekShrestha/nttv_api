from abc import ABC, abstractmethod 

class IIdGenerator(ABC):

    @abstractmethod
    def generate_ticket_id(self) -> str: pass

    @abstractmethod
    def generate_ticket_activities_id(self) -> str: pass

    @abstractmethod
    def generate_ticket_assignment_id(self) -> str: pass

    @abstractmethod
    def generate_team_recipient_id(self) -> str: pass

    @abstractmethod
    def generate_agent_recipient_id(self) -> str: pass

    @abstractmethod
    def generate_random_id(self) -> str: pass
