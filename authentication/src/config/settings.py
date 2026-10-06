from dotenv import load_dotenv
import os

class Settings:

    def __init__(self) : 
        load_dotenv()

        self.DATABASE_URL= os.environ["DATABASE_URL"]
        self.ALEMBIC_DATABASE_URL = os.environ["ALEMBIC_DATABASE_URL"]
        self.JWT_SECRET_KEY= os.environ["JWT_SECRET_KEY"]
        self.JWT_ACCESS_EXPIRE_MINUTES: int = int(os.environ["JWT_ACCESS_EXPIRE_MINUTES"])
        self.REFRESH_EXPIRE_DAYS: int = int(os.environ["REFRESH_EXPIRE_DAYS"])
