from dataclasses import dataclass
from pydantic import BaseModel

class OTPResendEvent(BaseModel):
    email: str
    otp : str

