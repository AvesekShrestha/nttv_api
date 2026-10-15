from datetime import datetime

from pydantic import BaseModel

class JWTPayload(BaseModel):
    sub : str
    role : str

    iat: datetime
    exp: datetime
