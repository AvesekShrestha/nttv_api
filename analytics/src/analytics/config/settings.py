from dotenv import load_dotenv
import os


class Settings:
    def __init__(self):
        load_dotenv()

        self.DATABASE_URL = os.environ["DATABASE_URL"]
        self.ALEMBIC_DATABASE_URL = os.environ["ALEMBIC_DATABASE_URL"]
        self.FORWARD_POINTS = int(os.environ["FORWARD_POINTS"])
        self.ESCALATION_POINTS = int(os.environ["ESCALATION_POINTS"])
        self.RESOLUTION_SLA_BREACH_POINTS = int(os.environ["RESOLUTION_SLA_BREACH_POINTS"])
        self.ACKNOWLEDGEMENT_POINTS = int(os.environ["ACKNOWLEDGEMENT_POINTS"])
        self.RESOLUTION_POINTS = int(os.environ["RESOLUTION_POINTS"])
        self.MAX_RETRY_ATTEMPTS=int(os.environ["MAX_RETRY_ATTEMPTS"]) | 5



