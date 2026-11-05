from datetime import datetime, timezone
import secrets

from src.application.shared.id_generator_interface import IIdGenerator


class IdGenerator(IIdGenerator):
    def generate_notification_id(self) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        random_part = secrets.token_hex(4).upper()

        return f"NOT-{timestamp}-{random_part}"
