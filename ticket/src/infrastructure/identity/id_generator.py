from datetime import datetime
import secrets

from src.application.shared.id_generator_interface import IIdGenerator


class IdGenerator(IIdGenerator):

    def generate_ticket_id(self) -> str:

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        random_part = secrets.token_hex(2).upper()

        return f"TKT-{timestamp}-{random_part}"


    def generate_ticket_activities_id(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        random_part = secrets.token_hex(2).upper()

        return f"ACT-{timestamp}-{random_part}"


    def generate_ticket_assignment_id(self) -> str:

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        random_part = secrets.token_hex(2).upper()

        return f"ASGN-{timestamp}-{random_part}"


    def generate_team_recipient_id(self) -> str:

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        random_part = secrets.token_hex(2).upper()

        return f"TEAM-RCPT-{timestamp}-{random_part}"

    def generate_agent_recipient_id(self) -> str:

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        random_part = secrets.token_hex(2).upper()

        return f"AGNT-RCPT-{timestamp}-{random_part}"

    def generate_random_id(self) -> str:
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        random_part = secrets.token_hex(2).upper()

        return f"RND-{timestamp}-{random_part}"
