from dotenv import load_dotenv
import os

class Settings:

    def __init__(self) : 
        load_dotenv()

        self.DATABASE_URL= os.environ["DATABASE_URL"]
        self.ALEMBIC_DATABASE_URL = os.environ["ALEMBIC_DATABASE_URL"]
        self.JWT_SECRET_KEY= os.environ["JWT_SECRET_KEY"]
        self.ACKNOWLEDGEMENT_DEADLINE_IN_HOURS=int(os.environ["ACKNOWLEDGEMENT_DEADLINE_IN_HOURS"])
        self.RESOLUTION_DEADLINE_IN_HOURS=int(os.environ["RESOLUTION_DEADLINE_IN_HOURS"])
        self.ORGANIZATION_SERVICE_URL=os.environ["ORGANIZATION_SERVICE_URL"]

