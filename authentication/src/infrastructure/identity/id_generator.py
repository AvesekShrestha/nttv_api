from datetime import datetime
import secrets

from src.application.shared.id_generator_interface import IIdGenerator


class IdGenerator(IIdGenerator):

    def generate_user_id(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        random_part = secrets.token_hex(2).upper()

        return f"USR-{timestamp}-{random_part}"

    def generate_team_member_id(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        random_part = secrets.token_hex(2).upper()

        return f"TKT-{timestamp}-{random_part}"

    def generate_team_id(self) -> str:

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        random_part = secrets.token_hex(2).upper()

        return f"TEAM-{timestamp}-{random_part}"

    def generate_refresh_token_id(self) -> str:

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        random_part = secrets.token_hex(2).upper()

        return f"RFT-{timestamp}-{random_part}"

    def generate_category_id(self) -> str:

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        random_part = secrets.token_hex(2).upper()

        return f"CAT-{timestamp}-{random_part}"

    def generate_random_id(self) -> str:
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        random_part = secrets.token_hex(2).upper()

        return f"RND-{timestamp}-{random_part}"

